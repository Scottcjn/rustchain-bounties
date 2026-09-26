"""Root conftest: ensure optional third-party imports resolve during tests.

If the real `prometheus_client` package is unavailable, importing
`scripts.prometheus_exporter` installs its minimal functional fallback into
`sys.modules`, so test modules that import `prometheus_client` directly
(e.g. `tests/test_prometheus_metrics_exporter.py`) still collect and pass.
When the real package is installed this is a no-op.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))

try:
    import prometheus_client  # noqa: F401
except ImportError:
    import prometheus_exporter  # noqa: F401  (registers the fallback stub)
