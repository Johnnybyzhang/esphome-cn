"""ESPHome package initialization with GitHub URL rewriting."""

# Importing applies monkeypatches for GitHub requests using dowhen.
from . import github_mirror  # noqa: F401
