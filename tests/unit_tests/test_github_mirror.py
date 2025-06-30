import os
from esphome.github_mirror import _transform_url, CUSTOM_URL, _patch_popen


def test_transform_url_git_plus():
    url = "git+https://github.com/maxgerhardt/platform-raspberrypi.git"
    expected = f"git+{CUSTOM_URL}/https://github.com/maxgerhardt/platform-raspberrypi.git"
    assert _transform_url(url) == expected


def test_transform_url_already_patched():
    url = f"git+{CUSTOM_URL}/https://github.com/example/repo.git"
    assert _transform_url(url) == url


def test_patch_popen_list():
    args = ["git", "clone", "https://github.com/example/repo.git"]
    result = _patch_popen(args)
    assert result["args"][2] == f"{CUSTOM_URL}/https://github.com/example/repo.git"


def test_patch_popen_string():
    cmd = "git clone https://github.com/example/repo.git"
    result = _patch_popen(cmd)
    assert f"{CUSTOM_URL}/https://github.com/example/repo.git" in result["args"]
