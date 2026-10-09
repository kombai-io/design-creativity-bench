"""UIClip image embeddings of segment screenshots, the second encoder of the hybrid score.

Model: biglab/uiclip_jitteredwebsites-2-224-paraphrased_webpairs_humanpairs (UIClip ViT-B/32,
fine-tuned on human design-pair judgements). Each screenshot is placed at native scale, top-left,
on a 1280x1280 neutral square (cropped past it), JPEG-encoded, then resized to 224x224 and
normalised with the CLIP statistics. One L2-normalised 512-d vector per segment.

Runs in-process on CPU or GPU, or against a server exposing the same /embed contract.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

import numpy as np

from .embedding import CANVAS_BACKGROUND, encode_jpeg, hex_to_rgb

MODEL = "biglab/uiclip_jitteredwebsites-2-224-paraphrased_webpairs_humanpairs"
PROCESSOR = "openai/clip-vit-base-patch32"
SIDE = 1280
SIZE = 224
BATCH = 64


def shape_pad_native(path: Path) -> bytes:
  """Native scale, top-left, on a neutral square; anything past the square is cropped."""
  from PIL import Image
  with Image.open(path) as image:
    image = image.convert("RGB").crop((0, 0, min(image.width, SIDE), min(image.height, SIDE)))
    ground = Image.new("RGB", (SIDE, SIDE), hex_to_rgb(CANVAS_BACKGROUND))
    ground.paste(image, (0, 0))
    return encode_jpeg(ground, 85)


class Local:
  def __init__(self) -> None:
    import torch
    from transformers import CLIPImageProcessor, CLIPModel
    self.torch = torch
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    self.dtype = torch.float16 if self.device == "cuda" else torch.float32
    processor = CLIPImageProcessor.from_pretrained(PROCESSOR)
    self.mean = torch.tensor(processor.image_mean, device=self.device).view(1, 3, 1, 1)
    self.sd = torch.tensor(processor.image_std, device=self.device).view(1, 3, 1, 1)
    self.model = CLIPModel.from_pretrained(MODEL).eval().to(self.device, self.dtype)

  def embed(self, blobs: list[bytes]) -> np.ndarray:
    from PIL import Image
    torch = self.torch
    out = []
    with torch.inference_mode():
      for start in range(0, len(blobs), BATCH):
        crops = []
        for blob in blobs[start:start + BATCH]:
          image = Image.open(io.BytesIO(blob))
          image.draft("RGB", (SIZE, SIZE))
          crops.append(np.asarray(image.convert("RGB").resize((SIZE, SIZE)), dtype=np.uint8))
        pixels = torch.from_numpy(np.stack(crops)).to(self.device).permute(0, 3, 1, 2).float().div_(255)
        features = self.model.get_image_features(pixel_values=((pixels - self.mean) / self.sd).to(self.dtype))
        features = (features if torch.is_tensor(features) else features.pooler_output).float()
        out.append((features / features.norm(dim=-1, keepdim=True).clamp_min(1e-12)).cpu().numpy())
    return np.concatenate(out) if out else np.zeros((0, 512), dtype=np.float32)


class Remote:
  """A server that takes {"images": [b64 jpeg], "variants": [{"model", "policy": "squash"}]}."""

  def __init__(self, endpoint: str) -> None:
    self.endpoint = endpoint.rstrip("/")

  def embed(self, blobs: list[bytes]) -> np.ndarray:
    import httpx
    out = []
    with httpx.Client(timeout=300) as client:
      for start in range(0, len(blobs), 16):
        payload = {"images": [base64.b64encode(b).decode() for b in blobs[start:start + 16]],
                   "variants": [{"model": "uiclip_humanpairs", "policy": "squash"}], "max_windows": 8}
        response = client.post(f"{self.endpoint}/embed", json=payload)
        response.raise_for_status()
        out.extend(response.json()["embeddings"]["uiclip_humanpairs/squash"])
    return np.asarray(out, dtype=np.float32)


def embed_design(design: Path, encoder: Local | Remote) -> int:
  """Write uiclip/<kid>.npy for every captured segment that lacks one."""
  target = design / "uiclip"
  target.mkdir(exist_ok=True)
  clips = [p for p in sorted((design / "segments").glob("*.jpg")) if not (target / f"{p.stem}.npy").is_file()]
  if not clips:
    return 0
  vectors = encoder.embed([shape_pad_native(p) for p in clips])
  for clip, vector in zip(clips, vectors):
    np.save(target / f"{clip.stem}.npy", vector.astype(np.float32))
  return len(clips)
