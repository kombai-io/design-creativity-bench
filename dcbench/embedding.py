"""gemini-embedding-2 image embeddings of segment screenshots.

Every screenshot is first scaled uniformly (never stretched) to fit a 1280x448 canvas and padded
top-left onto a neutral ground, so a segment's aspect ratio survives the embedder's own resize.

Credentials come from the environment, as google-genai reads them: GEMINI_API_KEY (or
GOOGLE_API_KEY) for the Gemini API, or GOOGLE_GENAI_USE_VERTEXAI=true with GOOGLE_CLOUD_PROJECT and
GOOGLE_CLOUD_LOCATION for Vertex AI.
"""
from __future__ import annotations

import io
from pathlib import Path
import random
import time
from typing import Any

import numpy as np

EMBEDDING_MODEL = "gemini-embedding-2"
DIMENSIONS = 1536
JPEG_QUALITY = 85
CANVAS_BACKGROUND = "#f4f5f7"
CANVAS_SHAPE = (1280, 448)
CANVAS_ANCHOR = "topleft"

RETRYABLE_MARKERS = ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500", "INTERNAL", "DEADLINE_EXCEEDED")
MAX_ATTEMPTS = 6
BACKOFF_BASE_SECONDS = 2.0


def client() -> Any:
  from google import genai
  return genai.Client()


def encode_jpeg(image: Any, quality: int) -> bytes:
  buffer = io.BytesIO()
  image.convert("RGB").save(buffer, "JPEG", quality=quality)
  return buffer.getvalue()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
  value = value.lstrip("#")
  return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def on_canvas(image: Any, shape: tuple[int, int] = CANVAS_SHAPE, anchor: str = CANVAS_ANCHOR,
              background: str = CANVAS_BACKGROUND) -> Any:
  """One screenshot, scaled uniformly to fit `shape` and padded onto it (upscaling allowed)."""
  from PIL import Image

  canvas_width, canvas_height = shape
  scale = min(canvas_width / image.width, canvas_height / image.height)
  width = max(1, min(canvas_width, round(image.width * scale)))
  height = max(1, min(canvas_height, round(image.height * scale)))
  resized = image.convert("RGB").resize((width, height), Image.LANCZOS)
  canvas = Image.new("RGB", (canvas_width, canvas_height), hex_to_rgb(background))
  offset = (0, 0) if anchor == "topleft" else ((canvas_width - width) // 2, (canvas_height - height) // 2)
  canvas.paste(resized, offset)
  return canvas


def canvas_bytes(jpeg_path: Path) -> bytes:
  """The bytes sent to the embedder for one segment; the stored .jpg stays the raw screenshot."""
  from PIL import Image

  with Image.open(jpeg_path) as image:
    image.load()
    return encode_jpeg(on_canvas(image), JPEG_QUALITY)


def embed_bytes(genai_client: Any, data: bytes, label: str) -> np.ndarray:
  """One image in, one vector out, retrying throttling with jittered backoff."""
  from google.genai import types

  parts = [types.Part.from_bytes(data=data, mime_type="image/jpeg")]
  for attempt in range(1, MAX_ATTEMPTS + 1):
    try:
      response = genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[types.Content(parts=parts)],
        config=types.EmbedContentConfig(output_dimensionality=DIMENSIONS),
      )
    except Exception as error:  # noqa: BLE001 - decided by the message, re-raised below
      if attempt == MAX_ATTEMPTS or not any(marker in str(error) for marker in RETRYABLE_MARKERS):
        raise
      time.sleep(BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)) * (0.5 + random.random()))
      continue
    if not response.embeddings or len(response.embeddings) != 1:
      received = len(response.embeddings) if response.embeddings else 0
      raise ValueError(f"Expected 1 embedding for {label}, received {received}")
    return np.asarray(response.embeddings[0].values, dtype=np.float32)
  raise RuntimeError(f"Unreachable retry exit for {label}")
