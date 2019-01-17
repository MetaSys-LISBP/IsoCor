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
                                   "charge": 1},
                                   {"formula": "C20",
                                   "nC": 20,
                                   "resolution": 100000,
                                   "charge": 1},
                                   {"formula": "C20",
                                   "nC": 20,
                                   "resolution": 100000,
                                   "charge": 2}])
def test_m_min_orbitrap(data, data_iso):
    """Calculation of the minimal *mass* difference (m_min) required to resolve two isotopic species
    of a labeled chemical at different resolution (10000, 100000) & charge (1, 2) on an *Orbitrap*.
    m_min calculated by IsoCor is compared to the expected value (provided in the fixture) and to the
    theoretical value (equation provided in the code).
    This is checked for correctors instantiated through the Factory or directly as HighResMetaboliteCorrector. 
    """
    charge = data["charge"]
    mw = data["nC"]*float(data_iso["C"]["mass"][0])
    mz = mw/charge
    # Theoretical mmin 
    m_min_th = 1.66 * (mw/charge)**(3/2)/(data["resolution"]*math.sqrt(400))*charge
    # Estimated mmin
    #    when metabolite is instantiated directly as HighResMetaboliteCorrector
    metabolite_hr = hrcor.HighResMetaboliteCorrector(data["formula"], "13C", data_isotopes=data_iso,
                                                  resolution=data["resolution"],
                                                  resolution_formula_code="orbitrap",
                                                  derivative_formula=None,
                                                  mz_of_resolution=400,
                                                  correct_NA_tracer=False,
                                                  tracer_purity=[0.0, 1.0],
                                                  charge=charge)
    m_min_isocor_hr = float(metabolite_hr._correction_limit)
    #    when metabolite is instantiated through the Factory
    metabolite_factory = hrcor.MetaboliteCorrectorFactory(data["formula"], "13C", data_isotopes=data_iso,
                                                  resolution=data["resolution"],
                                                  resolution_formula_code="orbitrap",
                                                  derivative_formula=None,
                                                  mz_of_resolution=400,
                                                  correct_NA_tracer=False,
                                                  tracer_purity=[0.0, 1.0],
                                                  charge=charge)
    m_min_isocor_factory = float(metabolite_factory._correction_limit)
    # Compare estimated, theoretical and expected minimal mass difference to resolve two isotopic species
    np.testing.assert_allclose(m_min_isocor_hr, m_min_th, rtol=1e-7, atol=1e-7)
    np.testing.assert_allclose(m_min_isocor_factory, m_min_th, rtol=1e-7, atol=1e-7)
