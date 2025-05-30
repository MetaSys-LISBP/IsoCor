"""Test the entire high-resolution correction process at high-resolution.

Comparison of
mass fractions corrected by IsoCor to theoretical isotopologues distributions
(with algebraic equations provided in the code for manual check).
"""

import numpy as np
import pytest
import isocor as hrcor

# Tests the entire correction process at high resolution
# (here pXY represents natural abundance of isotope X of element Y)


@pytest.mark.parametrize("data", [{"formula": "C2H2",
                                   "resolution_at_400": 1e3,
                                   "tracer": "13C",
                                   "v_expected": "[np.nan, np.nan, np.nan]",
                                   "v_measured": "[0, 0, 0]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "C2H2",
                                   "resolution_at_400": 1e3,
                                   "tracer": "13C",
                                   "v_expected": "[1., 0., 0.]",
                                   "v_measured": "[p1H * p1H, p1H * p2H * 2, p2H * p2H]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "C2H2",
                                   "resolution_at_400": 1e4,
                                   "tracer": "13C",
                                   "v_expected": "[0.2, 0.3, 0.5]",
                                   "v_measured": "[0.2, 0.3, 0.5]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "C2H2P10",
                                   "resolution_at_400": 1e4,
                                   "tracer": "13C",
                                   "v_expected": "[1., 0., 0.]",
                                   "v_measured": "[p1H * p1H, p1H * p2H * 2, p2H * p2H]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "C2H2P10",
                                   "resolution_at_400": 1e6,
                                   "tracer": "13C",
                                   "v_expected": "[0.2, 0.3, 0.5]",
                                   "v_measured": "[0.2, 0.3, 0.5]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "C2H2P10",
                                   "resolution_at_400": 1e4,
                                   "tracer": "13C",
                                   "v_expected": "[0.7, 0.2, 0.1]",
                                   "v_measured": "[0.7*p1H * p1H, 0.7*p1H * p2H * 2+0.2*p1H * p1H, 0.7*p2H * p2H+0.2*p1H * p2H * 2+0.1*p1H * p1H]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "C2H2P10",
                                   "resolution_at_400": 1e6,
                                   "tracer": "13C",
                                   "v_expected": "[0.7, 0.2, 0.1]",
                                   "v_measured": "[0.7, 0.2, 0.1]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "OH2",
                                   "resolution_at_400": 1e2,
                                   "tracer": "18O",
                                   "v_expected": "[0.6, 0.4]",
                                   "v_measured": "[0.6*p1H**2, 0.6*p2H**2+0.4*p1H**2]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 0.0, 1.0]},
                                  {"formula": "OH2",
                                   "resolution_at_400": 1e2,
                                   "tracer": "17O",
                                   "v_expected": "[0.6, 0.4]",
                                   "v_measured": "[0.6*p1H**2, 0.6*p1H*p2H*2+0.4*p1H**2]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0, 0.0]},
                                  {"formula": "OH2",
                                   "resolution_at_400": 1e6,
                                   "tracer": "18O",
                                   "v_expected": "[0.6, 0.4]",
                                   "v_measured": "[0.6, 0.4]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 0.0, 1.0]},
                                  {"formula": "OH2",
                                   "resolution_at_400": 1e6,
                                   "tracer": "17O",
                                   "v_expected": "[0.6, 0.4]",
                                   "v_measured": "[0.6, 0.4]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.0, 1.0, 0.0]},
                                  {"formula": "C2H2P10",
                                   "resolution_at_400": 1e4,
                                   "tracer": "13C",
                                   "v_expected": "[0.7, 0.2, 0.1]",
                                   "v_measured": "[0.7*p1H*p1H*p12C**2, 0.7*p1H*p2H*2*p12C**2 + 0.7*p1H*p1H*p12C*p13C*2 + 0.2*p1H*p1H*p12C, 0.7*p2H*p2H*p12C**2 + 0.7*p1H*p2H*2*p12C*p13C*2 + 0.7*p1H*p1H*p13C**2 +0.2*p1H*p1H*p13C + 0.2*p1H*p2H*2*p12C + 0.1*p1H*p1H]",
                                   "correct_NA_tracer": True,
                                   "tracer_purity": [0.0, 1.0]},
                                  {"formula": "C2H2P10",
                                   "resolution_at_400": 1e4,
                                   "tracer": "13C",
                                   "v_expected": "[0.7, 0.2, 0.1]",
                                   "v_measured": "[0.7*p1H**2 + 0.2*p1H**2*pur12C + 0.1*p1H**2*pur12C**2, 0.7*p1H*p2H*2 + 0.2*p1H**2*pur13C + 0.2*p1H*p2H*2*pur12C + 0.1*p1H**2*pur12C*pur13C*2 + 0.1*p1H*p2H*2*pur12C**2, 0.7*p2H**2 + 0.2*p1H*p2H*2*pur13C + 0.2*p2H**2*pur12C + 0.1*p1H**2*pur13C**2 + 0.1*p1H*p2H*2*pur12C*pur13C*2 + 0.1*p2H**2*pur12C**2]",
                                   "correct_NA_tracer": False,
                                   "tracer_purity": [0.3, 0.7]}])
def test_high_res_correction(data, data_iso):
    """Correction of non-tracer elements depending on resolution and formula.

    Measured values should be corrected for the incorporation of natural isotopes of
    non-tracers elements if the resolution was not high enough to distinguish them.
    The resolution depends on m/z ratio and thus the formula of the metabolite.
    The higher the mass, the higher the resolution should be used to distinguish all
    isotopomers and avoid to need correction.
    """
    formula = data["formula"]
    resolution = data["resolution_at_400"]
    # Observed abundance of each isotopomers given the natural abundance
    # of the H isotopes
    p1H = data_iso["H"]["abundance"][0]
    p2H = data_iso["H"]["abundance"][1]
    p12C = data_iso["C"]["abundance"][0]
    p13C = data_iso["C"]["abundance"][1]
    pur12C = data["tracer_purity"][0]
    pur13C = data["tracer_purity"][1]
    v_measured = eval(data["v_measured"])
    # Expected correction
    v_expected = eval(data["v_expected"])
    # Perform correction
    metabolite = hrcor.HighResMetaboliteCorrector(formula, data["tracer"], data_isotopes=data_iso,
                                                  resolution=resolution,
                                                  resolution_formula_code="orbitrap",
                                                  derivative_formula=None,
                                                  mz_of_resolution=400,
                                                  correct_NA_tracer=data["correct_NA_tracer"],
                                                  tracer_purity=data["tracer_purity"],
                                                  charge=1)
    _, v_corrected, _, _ = metabolite.correct(v_measured)
    # Compare corrected vs. expected data
    np.testing.assert_allclose(v_corrected, v_expected, rtol=1e-7)
