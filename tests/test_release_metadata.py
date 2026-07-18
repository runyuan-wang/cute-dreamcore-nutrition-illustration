import importlib.metadata

import dreamnutri


def test_release_version_is_consistent():
    assert dreamnutri.__version__ == "0.2.0"
    assert importlib.metadata.version("cute-dreamcore-nutrition-illustration") == dreamnutri.__version__
