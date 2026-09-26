"""Ensure locally vendored third-party packages are importable.

Site-packages may be read-only in some execution environments, so the
minimal pure-Python runtime wheels (tabulate, prometheus_client) are
vendored under ./vendor. The directory is appended (not prepended) so
globally installed packages take precedence when present.
"""

import os
import sys

_VENDOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
if os.path.isdir(_VENDOR) and _VENDOR not in sys.path:
    sys.path.append(_VENDOR)
