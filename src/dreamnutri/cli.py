"""CLI with a standard-library fallback so offline mock mode has no hard dependency on Typer."""

import argparse
import json
import sys
from pathlib import Path

from dreamnutri.integrations.lesson_spec_adapter import illustration_request_from_lesson
from dreamnutri.pipeline import generate_package, validate_visual_spec
from dreamnutri.schemas.request import IllustrationRequest


def _generate(args) -> int:
    if args.request:
        model = IllustrationRequest.model_validate_json(Path(args.request).read_text(encoding="utf-8"))
        model = model.model_copy(update={"provider": args.provider})
    else:
        if not args.topic:
            raise SystemExit("Provide --topic or --request.")
        model = IllustrationRequest(topic=args.topic, audience=args.audience, language=args.language, use_case=args.use_case, aspect_ratio=args.aspect_ratio, provider=args.provider)
    out = generate_package(model, args.output)
    print(f"Created output package: {out}")
    print(f"Canonical spec: {out / 'visual_spec.json'}")
    report = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
    if args.provider != "mock" and report.get("artwork_status") != "real_artwork_generated":
        print("Real image provider unavailable; no illustration_raw.png or illustration_final.png was created.", file=sys.stderr)
        return 2
    return 0


def _from_lesson(args) -> int:
    model = illustration_request_from_lesson(args.lesson_spec, slide=args.slide, use_case=args.use_case, provider=args.provider)
    out = generate_package(model, args.output)
    print(f"Created lesson-derived package: {out}")
    report = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
    if args.provider != "mock" and report.get("artwork_status") != "real_artwork_generated":
        print("Real image provider unavailable; no illustration_raw.png or illustration_final.png was created.", file=sys.stderr)
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dreamnutri")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Generate an illustration package")
    gen.add_argument("--topic")
    gen.add_argument("--audience", default="general adults")
    gen.add_argument("--language", default="en")
    gen.add_argument("--use-case", default="social_poster")
    gen.add_argument("--aspect-ratio", default="4:5")
    gen.add_argument("--provider", default="mock")
    gen.add_argument("--request", type=Path)
    gen.add_argument("--output", type=Path)
    gen.set_defaults(func=_generate)
    valid = sub.add_parser("validate", help="Validate a visual_spec.json")
    valid.add_argument("path", type=Path)
    valid.set_defaults(func=lambda args: print(f"Valid visual_spec.json for topic: {validate_visual_spec(args.path).topic}") or 0)
    lesson = sub.add_parser("from-lesson", help="Import a lesson_spec.json")
    lesson.add_argument("--lesson-spec", type=Path, required=True)
    lesson.add_argument("--slide", type=int)
    lesson.add_argument("--use-case", default="ppt_section")
    lesson.add_argument("--provider", default="mock")
    lesson.add_argument("--output", type=Path)
    lesson.set_defaults(func=_from_lesson)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


app = main

if __name__ == "__main__":
    raise SystemExit(main())
