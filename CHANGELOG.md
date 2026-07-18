# Changelog

## 0.2.0

- Fixed the `from-lesson` CLI mock path so it exits cleanly after generating its package.
- Kept citations optional and removed medical-keyword content blocking from the image renderer; upstream authors own content review.
- Aligned package and generated-spec version metadata with the 0.2.0 release.
- Renamed mock outputs to `layout_mock_preview.png` and `text_overlay_mock_preview.png`.
- Prevented mock and unavailable-provider runs from creating `illustration_final.png`.
- Added explicit artwork status, style-fidelity status, provider failure reporting, and comparison contact sheets.
- Added real-provider dimension inspection and manual-review-required style-fidelity checklist.

## 0.1.0

- Initial offline MVP.
- Canonical `visual_spec.json` pipeline.
- Dietary fiber and gut health curated example.
- Deterministic mock provider and Pillow text overlay.
- Optional isolated image-provider adapter.
- External `lesson_spec.json` adapter.
