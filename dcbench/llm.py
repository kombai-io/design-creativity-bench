"""One forced tool call through the OpenAI Responses API, with validation and retry.

Used by the colour extractor. Reads OPENAI_API_KEY from the
environment (and OPENAI_BASE_URL, if set).
"""
from __future__ import annotations

import base64
import json
from typing import Any, Callable

from pydantic import BaseModel


def image_part(data: bytes, media_type: str = "image/jpeg") -> dict:
  return {"type": "input_image", "image_url": f"data:{media_type};base64,{base64.b64encode(data).decode()}"}


def text_part(text: str) -> dict:
  return {"type": "input_text", "text": text}


def call_tool(
  model: str,
  system: str,
  content: list[dict],
  tool_name: str,
  description: str,
  schema: type[BaseModel],
  effort: str,
  check: Callable[[BaseModel], str | None] = lambda parsed: None,
  iterations: int = 3,
) -> BaseModel:
  """Ask `model` to call `tool_name` once; return the parsed arguments.

  `check` returns an error message for arguments that parse but are incomplete; the message goes
  back to the model as the tool's result and it is asked again, up to `iterations` turns.
  """
  from openai import OpenAI

  client = OpenAI()
  tool = {"type": "function", "name": tool_name, "description": description,
          "parameters": schema.model_json_schema(), "strict": False}
  request: dict[str, Any] = {
    "model": model, "instructions": system, "tools": [tool],
    "tool_choice": {"type": "function", "name": tool_name},
    "reasoning": {"effort": effort},
    "input": [{"role": "user", "content": content}],
  }
  last_error = "no tool call"
  for _ in range(iterations):
    response = client.responses.create(**request)
    calls = [item for item in response.output if item.type == "function_call" and item.name == tool_name]
    if not calls:
      last_error = "the model did not call the tool"
      request = {**request, "previous_response_id": response.id,
                 "input": [{"role": "user", "content": [text_part(f"You must call the {tool_name} tool.")]}]}
      continue
    call = calls[-1]
    try:
      parsed = schema.model_validate(json.loads(call.arguments))
      problem = check(parsed)
    except Exception as error:  # noqa: BLE001 - reported back to the model
      problem = f"Invalid arguments: {error}"
    if problem is None:
      return parsed
    last_error = problem
    request = {**request, "previous_response_id": response.id,
               "input": [{"type": "function_call_output", "call_id": call.call_id, "output": problem}]}
  raise ValueError(f"{tool_name}: no valid call after {iterations} turns ({last_error})")
