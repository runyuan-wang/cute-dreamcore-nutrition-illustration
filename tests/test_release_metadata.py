import importlib.metadata
from pathlib import Path

import dreamnutri


def test_release_version_is_consistent():
    assert dreamnutri.__version__ == "0.2.0"
    assert importlib.metadata.version("cute-dreamcore-nutrition-illustration") == dreamnutri.__version__


def test_public_identity_is_present_in_package_and_both_readmes():
    root = Path(__file__).resolve().parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    readme_en = (root / "README.md").read_text(encoding="utf-8")
    readme_zh = (root / "README.zh-CN.md").read_text(encoding="utf-8")
    assert 'name = "Wang Runyuan"' in pyproject
    assert 'email = "jykmsg@163.com"' in pyproject
    assert "Wang Runyuan (王润圆)" in readme_en
    assert "王润圆 (Wang Runyuan)" in readme_zh
    assert "Chinese Registered Dietitian" in readme_en
    assert "中国注册营养师" in readme_zh


def test_sdist_manifest_keeps_skill_and_readme_assets():
    root = Path(__file__).resolve().parents[1]
    manifest = (root / "MANIFEST.in").read_text(encoding="utf-8")
    assert "include SKILL.md" in manifest
    assert "include README.zh-CN.md" in manifest
    assert "recursive-include docs/images *.png *.jpg *.jpeg" in manifest
    assert "recursive-include style *.md" in manifest
    assert "recursive-include templates *.json" in manifest
    assert "prune outputs" in manifest
    assert "global-exclude __pycache__" in manifest
