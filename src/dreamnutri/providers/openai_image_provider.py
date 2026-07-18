import base64
import os
from pathlib import Path

from PIL import Image

from .base import ImageProvider, ProviderError, ProviderResult


class OpenAIImageProvider(ImageProvider):
    name = "openai"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.endpoint = os.getenv("OPENAI_IMAGE_ENDPOINT", "https://api.openai.com/v1/images/generations")
        self.timeout = float(os.getenv("OPENAI_IMAGE_TIMEOUT_SECONDS", "120"))
        self.default_model = os.getenv("OPENAI_IMAGE_MODEL") or None

    def generate(self, prompt: str, negative_prompt: str, width: int, height: int, output_path: Path, seed: int | None = None, model: str | None = None) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is required for provider=openai; no request was sent.")
        try:
            import httpx
        except ImportError as exc:
            raise ProviderError("Install the optional httpx dependency before using provider=openai.") from exc
        selected_model = model or self.default_model
        if not selected_model:
            raise ProviderError("Set OPENAI_IMAGE_MODEL or pass an explicit model; the adapter will not guess a model.")
        size = os.getenv("OPENAI_IMAGE_SIZE", "auto")
        payload = {"model": selected_model, "prompt": f"{prompt}\nNegative prompt: {negative_prompt}", "size": size, "n": 1, "output_format": "png"}
        try:
            response = httpx.post(self.endpoint, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as exc:
            raise ProviderError(f"Image provider timed out after {self.timeout:g}s.") from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"Image provider request failed: {exc}") from exc
        image_data = (data.get("data") or [{}])[0]
        if image_data.get("b64_json"):
            content = base64.b64decode(image_data["b64_json"])
        elif image_data.get("url"):
            download = httpx.get(image_data["url"], timeout=self.timeout)
            download.raise_for_status()
            content = download.content
        else:
            raise ProviderError("Image provider returned no b64_json or url image payload.")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            from io import BytesIO
            image = Image.open(BytesIO(content)).convert("RGB")
            image.save(output_path, format="PNG")
        except Exception as exc:
            raise ProviderError("Image provider returned bytes that could not be decoded as an image.") from exc
        return ProviderResult(raw_path=output_path, provider=self.name, requested_model=selected_model, actual_model=data.get("model"), response_id=data.get("id"), seed=seed, returned_dimensions=image.size, metadata={"requested_size": size, "response_keys": sorted(data.keys())})
