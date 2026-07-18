#!/usr/bin/env python3
"""Manual-only real provider smoke test; never run in the default test suite."""

from pathlib import Path

from dreamnutri.pipeline import generate_package
from dreamnutri.schemas.request import IllustrationRequest


if __name__ == "__main__":
    request = IllustrationRequest.model_validate_json(Path("examples/dietary-fiber-gut-health/request.json").read_text()).model_copy(update={"provider": "openai"})
    output = generate_package(
        request,
        Path("outputs/manual-real-provider"),
    )
    print(output)
