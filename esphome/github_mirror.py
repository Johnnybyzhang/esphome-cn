import os

from dowhen import when
import requests

try:
    from platformio.http import HTTPClient, HTTPSession
    from platformio.package.vcsclient import VCSClientFactory
except Exception:  # pragma: no cover
    HTTPSession = None
    HTTPClient = None
    VCSClientFactory = None

import subprocess

# Base URL used as prefix for GitHub requests
CUSTOM_URL = os.environ.get("CUSTOM_GITHUB_URL", "https://gh.161024.xyz")


def _transform_url(url: str) -> str:
    """Prefix GitHub URLs with the custom mirror."""
    if url.startswith(CUSTOM_URL):
        return url
    if "github.com" in url:
        return f"{CUSTOM_URL}/{url}"
    return url


# Patch requests.Session.request
def _patch_requests(url):
    new_url = _transform_url(url)
    if new_url != url:
        return {"url": new_url}


when(requests.sessions.Session.request, "<start>").do(_patch_requests)


def _patch_subprocess(cmd, *args, **kwargs):
    if (
        isinstance(cmd, (list, tuple))
        and len(cmd) >= 3
        and cmd[1:3] == ["-m", "pip"]
        and cmd[3:4] == ["list"]
    ):
        return {"stdout": b"[]"}


when(subprocess.check_output, "<start>").do(_patch_subprocess)

if HTTPSession is not None:
    when(HTTPSession.request, "<start>").do(
        lambda self, method, url, *args, **kwargs: {"url": _transform_url(url)}
    )


# Patch git command execution
try:
    from esphome.git import run_git_command
except Exception:  # pragma: no cover
    run_git_command = None

if run_git_command is not None:

    def _patch_git(cmd):
        patched = False
        for i, arg in enumerate(cmd):
            if (
                isinstance(arg, str)
                and "github.com" in arg
                and not arg.startswith(CUSTOM_URL)
            ):
                cmd[i] = f"{CUSTOM_URL}/{arg}"
                patched = True
        if patched:
            return {"cmd": cmd}

    when(run_git_command, "<start>").do(_patch_git)

if VCSClientFactory is not None:
    when(VCSClientFactory.new, "<start>").do(
        lambda src_dir, remote_url, **kwargs: {"remote_url": _transform_url(remote_url)}
    )

if HTTPClient is not None:

    def _patch_httpclient_init(endpoints, **kwargs):
        if isinstance(endpoints, (list, tuple)):
            endpoints = [_transform_url(e) for e in endpoints]
        else:
            endpoints = _transform_url(endpoints)
        return {"endpoints": endpoints}

    when(HTTPClient.__init__, "<start>").do(
        lambda self, endpoints, *args, **kwargs: _patch_httpclient_init(
            endpoints, **kwargs
        )
    )

    when(HTTPClient.send_request, "<start>").do(
        lambda self, method, path, **kwargs: {"path": _transform_url(path)}
    )
