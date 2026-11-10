#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Package entry-point: ``python -m catalog_provider``."""

from catalog_provider.daemon import main
import sys

sys.exit(main())
