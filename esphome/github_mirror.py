import os
import re
import subprocess
import shlex
from pathlib import Path

from dowhen import when
import requests

try:
    from platformio.http import HTTPClient, HTTPSession
    from platformio.package.vcsclient import VCSClientFactory
except Exception:  # pragma: no cover
    HTTPSession = None
    HTTPClient = None
    VCSClientFactory = None

# Base URL used as prefix for GitHub requests
CUSTOM_URL = os.environ.get("CUSTOM_GITHUB_URL", "https://gh.161024.xyz")


def _transform_url(url: str) -> str:
    """Rewrite GitHub URLs using the custom mirror."""
    if CUSTOM_URL in url:
        return url

    def repl(match: re.Match) -> str:
        return f"{CUSTOM_URL}/{match.group(0)}"

    return re.sub(r"https?://[^\s]*github[^\s]*", repl, url)


# Patch requests.Session.request
def _patch_requests(url):
    new_url = _transform_url(url)
    if new_url != url:
        return {"url": new_url}


when(requests.sessions.Session.request, "<start>").do(_patch_requests)

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
            if isinstance(arg, str):
                new_arg = _transform_url(arg)
                if new_arg != arg:
                    cmd[i] = new_arg
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

# Patch generic git commands executed via subprocess
def _patch_popen(args, **kwargs):
    """Rewrite GitHub URLs when git commands are executed."""
    def _handle_list(lst):
        patched = False
        for i, arg in enumerate(lst):
            if isinstance(arg, str):
                new_arg = _transform_url(arg)
                if new_arg != arg:
                    lst[i] = new_arg
                    patched = True
        return patched

    # args can be a sequence or string
    if isinstance(args, (list, tuple)):
        if args and isinstance(args[0], str) and Path(args[0]).stem.lower() == "git":
            args = list(args)
            if _handle_list(args):
                return {"args": args}
    elif isinstance(args, str):
        parts = shlex.split(args)
        if parts and Path(parts[0]).stem.lower() == "git":
            if _handle_list(parts):
                args = " ".join(shlex.quote(p) for p in parts)
                return {"args": args}


when(subprocess.Popen.__init__, "<start>").do(_patch_popen)
