"""Test calculation of the minimal *mass* difference required to resolve two isotopic species
of a labeled chemical.

The minimal *mass* difference required to separate two isotopic species of a labeled chemical
correspond to the minimal difference of mz to distinguish two MS peaks at the operating resolution 
multiplied by the charge. The minimal mz difference is calculated at the operating 
resolution using 'resolution_formula' of orbitrap (Su et al., 2017) at the mz of the labeled chemical.
"""

import numpy as np
import pytest
import isocor as hrcor
import math

@pytest.mark.parametrize("data", [{"formula": "C20",
                                   "nC": 20,
                                   "resolution": 10000,
                                   "charge": 1,
                                   "m_min_expected": 0.03086},
                                   {"formula": "C20",
                                   "nC": 20,
                                   "resolution": 10000,
                                   "charge": 2,
                                   "m_min_expected": 0.021821},
                                   {"formula": "C20",
                                   "nC": 20,
                                   "resolution": 100000,
                                   "charge": 1,
                                   "m_min_expected": 0.003086},
                                   {"formula": "C20",
                                   "nC": 20,
                                   "resolution": 100000,
                                   "charge": 2,
                                   "m_min_expected": 0.0021821}])
def test_m_min_orbitrap(data, data_iso):
    """Calculation of the minimal *mass* difference (m_min) required to resolve two isotopic species
    of a labeled chemical at different resolution (10000, 100000) & charge (1, 2) on an *Orbitrap*.
    m_min calculated by IsoCor is compared to the expected value (provided in the fixture) and to the
    theoretical value (equation provided below).
    """
    charge = data["charge"]
    mw = data["nC"]*float(data_iso["C"]["mass"][0])
    mz = mw/charge
    # Expected mmin
    m_min_expected = data["m_min_expected"]
    # Theoretical mmin 
    m_min_th = 1.66 * (mw/charge)**(3/2)/(data["resolution"]*math.sqrt(400))*charge
    # Estimated mmin
    metabolite = hrcor.HighResMetaboliteCorrector(data["formula"], "13C", data_isotopes=data_iso,
                                                  resolution=data["resolution"],
                                                  resolution_formula_code="orbitrap",
                                                  derivative_formula=None,
                                                  mz_of_resolution=400,
                                                  correct_NA_tracer=False,
                                                  tracer_purity=[0.0, 1.0],
                                                  charge=charge)
    m_min_isocor = float(metabolite._correction_limit)
    # Compare estimated, theoretical and expected minimal mass difference to resolve two isotopic species
    np.testing.assert_allclose(m_min_isocor, m_min_expected, rtol=1e-7, atol=1e-7)
    np.testing.assert_allclose(m_min_isocor, m_min_th, rtol=1e-7, atol=1e-7)
    np.testing.assert_allclose(m_min_th, m_min_expected, rtol=1e-7, atol=1e-7)
