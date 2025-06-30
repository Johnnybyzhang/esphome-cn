import os
from esphome.github_mirror import _transform_url, CUSTOM_URL


def test_transform_url_git_plus():
    url = "git+https://github.com/maxgerhardt/platform-raspberrypi.git"
    expected = f"git+{CUSTOM_URL}/https://github.com/maxgerhardt/platform-raspberrypi.git"
    assert _transform_url(url) == expected


def test_transform_url_already_patched():
    url = f"git+{CUSTOM_URL}/https://github.com/example/repo.git"
    assert _transform_url(url) == url
