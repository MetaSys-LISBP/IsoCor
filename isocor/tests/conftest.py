"""Configuration variables for the tests

Shared pre-defined parameters
The return value of fixture function will be available as a predefined
parameter for all test functions. The test's parameter name must be the same as
the fixture function's name.
"""

import pytest
from decimal import Decimal as D
import numpy as np


@pytest.fixture
def data_iso():
    """Typical isotopic data object."""
    return {"C": {"abundance": [0.7, 0.3],
                  "mass": [D('12.0'), D('13.0033548378')]},
            "H": {"abundance": [0.8, 0.2],
                  "mass": [D('1.0078250321'), D('2.014101778')]},
            "N": {"abundance": [0.9, 0.1],
                  "mass": [D('14.0030740052'), D('15.0001088984')]},
            "P": {"abundance": [1.],
                  "mass": [D('30.97376151')]},
            "O": {"abundance": [0.6, 0.3, 0.1],
                  "mass": [D('15.9949146221'), D('16.9991315'), D('17.9991604')]}}

@pytest.fixture
def usr_tolerance():
    """Platform-dependent tolerance."""
    return 10**4*np.finfo(float).eps
