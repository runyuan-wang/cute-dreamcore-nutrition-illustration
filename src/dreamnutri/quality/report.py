def markdown_report(content: dict, visual: dict, provider: str, output_path: str, artwork_status: str, provider_error: str | None = None) -> str:
    def rows(section: dict) -> str:
        lines = []
        for key, value in section.items():
            lines.append(f"| {key} | {'PASS' if value is True else 'WARN' if value not in (False, True) else 'FAIL'} |")
        return "\n".join(lines)

    lines = [
        "# Dreamnutri Quality Report",
        "",
        f"- Provider: `{provider}`",
        f"- Output: `{output_path}`",
        f"- Content status: **{content['status']}**",
        f"- Visual status: **{visual['status']}**",
        f"- artwork_status: `{artwork_status}`",
        f"- style_fidelity_not_evaluated: `{str(visual.get('style_fidelity_not_evaluated', True)).lower()}`",
        f"- real_image_provider_required: `{str(artwork_status != 'real_artwork_generated').lower()}`",
        "",
        "## Scientific checks",
        "",
        "| Check | Result |\n|---|---|",
        rows(content["checks"]),
        "",
        "## Visual and accessibility checks",
        "",
        "| Check | Result |\n|---|---|",
        rows({**visual["checks"], **visual["accessibility"]}),
        "",
    ]
    if content.get("errors"):
        lines += ["## Errors", "", *[f"- {error}" for error in content["errors"]], ""]
    if content.get("warnings"):
        lines += ["## Warnings", "", *[f"- {warning}" for warning in content["warnings"]], ""]
    if provider_error:
        lines += ["## Provider status", "", f"- Real provider unavailable: {provider_error}", "- No real artwork was generated and no mock output was promoted to final artwork.", ""]
    lines += ["## Style-fidelity checklist", "", "A programmatic mock cannot pass this artistic checklist. Each real-artwork item requires manual visual inspection.", "", "| Item | Status |", "|---|---|"]
    lines.extend(f"| {key} | {value.get('status', 'unknown')} |" for key, value in visual.get("style_fidelity", {}).items())
    return "\n".join(lines)
