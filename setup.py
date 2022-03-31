# =====================================
# generator=datazen
# version=1.14.0
# hash=1bf7c9c92cde069b100f8ccfeb7b0d46
# =====================================

"""
vcorelib - Package definition for distribution.
"""

# third-party
try:
    from vmklib.setup import setup
except (ImportError, ModuleNotFoundError):
    from vcorelib_bootstrap.setup import setup  # type: ignore

# internal
from vcorelib import DESCRIPTION, PKG_NAME, VERSION

author_info = {
    "name": "Vaughn Kottler",
    "email": "vaughnkottler@gmail.com",
    "username": "vkottler",
}
pkg_info = {
    "name": PKG_NAME,
    "slug": PKG_NAME.replace("-", "_"),
    "version": VERSION,
    "description": DESCRIPTION,
    "versions": [
        "3.6",
        "3.7",
        "3.8",
        "3.9",
        "3.10",
    ],
}
setup(
    pkg_info,
    author_info,
)
