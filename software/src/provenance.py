"""Environment and version records written into every result file."""

from __future__ import annotations

import platform
import sys


def environment_record() -> dict:
    import matplotlib
    import numpy
    import scipy

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "matplotlib": matplotlib.__version__,
    }
