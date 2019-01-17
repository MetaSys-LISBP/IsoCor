"""Test high-resolution correction matrix when no isotopic species are resolved from the tracer isotopologues.

In this situation, the contribution of all elements and isotopes should be removed,
hence the high-resolution and low-resolution correction matrices should be the same.

The high-resolution correction matrix calculated by IsoCor is compared to

1. a theoretical correction matrix (with algebraic equations provided in the code for manual check), and
2. the low resolution correction matrix.
"""

import numpy as np
import pytest
import isocor as hrcor

# Test the correction matrix by comparison with theoretical matrices expressed using explicit functions (here pXY represents natural
# abundance of isotope X of element Y), which can be easily verified. The examples provided are simple enough for manual verification,
# yet they represent the many situations that can be encountered in the real world. Each situation is detailed in the field "comment".


@pytest.mark.parametrize("data", [{"comment": "13C tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 3 isotopes",
                                   "formula": "C2O2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e4,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p16O**2, 0.0, 0.0], [p17O*p16O*2, p16O**2, 0.0], [p17O*p17O+p18O*p16O*2, p17O*p16O*2, p16O**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e4,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2, 0.0, 0.0], [2*p1H*p2H, p1H**2, 0.0], [p2H**2, 2*p1H*p2H, p1H**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, with NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e4,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": True,
                                   "expected_matrix": "[[p1H**2*p12C**2, 0.0, 0.0], [2*p1H*p2H*p12C**2+2*p12C*p13C*p1H**2, p1H**2*p12C, 0.0], [p2H**2*p12C**2+2*p12C*p13C*p1H*p2H*2+p1H**2*p13C**2, p12C*p1H*p2H*2+p1H**2*p13C, p1H**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 2 elements with 2 isotopes",
                                   "formula": "C2H2N2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e4,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2*p14N**2, 0.0, 0.0], [2*p1H*p2H*p14N**2+2*p14N*p15N*p1H**2, p1H**2*p14N**2, 0.0], [p2H**2*p14N**2+2*p14N*p15N*p1H*p2H*2+p1H**2*p15N**2, 2*p1H*p2H*p14N**2+2*p14N*p15N*p1H**2, p1H**2*p14N**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, no NA of the tracer element, with purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e4,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2, p1H**2*pur_12C, p1H**2*pur_12C*pur_12C], [2*p1H*p2H, p1H**2*pur_13C+2*p1H*p2H*pur_12C, p1H**2*pur_12C*pur_13C*2+2*p1H*p2H*pur_12C*pur_12C], [p2H**2, 2*p1H*p2H*pur_13C+p2H**2*pur_12C, p2H**2*pur_12C*pur_12C+p1H**2*pur_13C*pur_13C+p1H*p2H*2*pur_13C*pur_12C*2]]",
                                   "tracer_purity": [0.1, 0.9]},
                                  {"comment": "13C tracer, with derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "C2",
                                   "resolution": 1e4,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2*p12C**2, 0.0, 0.0], [2*p1H*p2H*p12C**2+2*p12C*p13C*p1H**2, p1H**2*p12C**2, 0.0], [p2H**2*p12C**2+2*p12C*p13C*p1H*p2H*2+p1H**2*p13C**2, 2*p1H*p2H*p12C**2+2*p12C*p13C*p1H**2, p1H**2*p12C**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, with derivative, no NA of the tracer element, with purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "C2",
                                   "resolution": 1e4,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2*p12C**2, pur_12C*(p1H**2*p12C**2), p1H**2*p12C**2*pur_12C*pur_12C], [2*p1H*p2H*p12C**2 + 2*p12C*p13C*p1H**2, pur_13C*(p1H**2*p12C**2) + pur_12C*(2*p1H*p2H*p12C**2 + 2*p12C*p13C*p1H**2), pur_13C*(pur_12C*(p1H**2*p12C**2)) + pur_12C*(pur_13C*(p1H**2*p12C**2) + pur_12C*(2*p1H*p2H*p12C**2 + 2*p12C*p13C*p1H**2))], [p2H**2*p12C**2 + 2*p12C*p13C*p1H*p2H*2 + p1H**2*p13C**2, pur_13C*(2*p1H*p2H*p12C**2+2*p12C*p13C*p1H**2) + pur_12C*(p2H**2*p12C**2+2*p12C*p13C*p1H*p2H*2+p1H**2*p13C**2), pur_12C*(pur_13C*(2*p1H*p2H*p12C**2+2*p12C*p13C*p1H**2) + pur_12C*(p2H**2*p12C**2+2*p12C*p13C*p1H*p2H*2+p1H**2*p13C**2)) + pur_13C*(pur_13C*(p1H**2*p12C**2) + pur_12C*(2*p1H*p2H*p12C**2 + 2*p12C*p13C*p1H**2))]]",
                                   "tracer_purity": [0.1, 0.9]},
                                  {"comment": "17O tracer, no derivative, no NA of the tracer element, with purity of the tracer element, tracer with 3 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "CO",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e2,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": True,
                                   "expected_matrix": "[[p16O*p12C, 0.0], [p17O*p12C+p16O*p13C, p12C]]",
                                   "tracer_purity": [0.0, 1.0, 0.0]},
                                  {"comment": "17O tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "CO",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e2,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p12C, 0.0], [p13C, p12C]]",
                                   "tracer_purity": [0.0, 1.0, 0.0]},
                                  {"comment": "17O tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 3 isotopes, correct for NA of 0 elements",
                                   "formula": "O",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e2,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[1.0, 0.0], [0.0, 1.0]]",
                                   "tracer_purity": [0.0, 1.0, 0.0]},
                                  {"comment": "18O tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 3 isotopes, correct for NA of 0 elements",
                                   "formula": "O2",
                                   "tracer": "18O",
                                   "derivative_formula": "",
                                   "resolution": 1e2,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]",
                                   "tracer_purity": [0., 0., 1.0]},
                                  {"comment": "17O tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 3 isotopes, correct for NA of 0 elements",
                                   "formula": "O2",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e2,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]",
                                   "tracer_purity": [0., 1.0, 0.]},
                                  {"comment": "2H tracer, no derivative, NA of the tracer element, with purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "H2",
                                   "tracer": "2H",
                                   "derivative_formula": "",
                                   "resolution": 1e2,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": True,
                                   "expected_matrix": "[[p1H**2, p1H*pur1H, pur1H**2], [p1H*p2H*2, p1H*pur2H + p2H*pur1H, pur1H*pur2H*2], [p2H**2, p2H*pur2H, pur2H**2]]",
                                   "tracer_purity": [0.1, 0.9]},
                                  {"comment": "2H tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 0 elements",
                                   "formula": "H2",
                                   "tracer": "2H",
                                   "derivative_formula": "",
                                   "resolution": 1e2,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]",
                                   "tracer_purity": [0., 1.0]}])
def test_high_res_cor_matrix_unresolved(data, data_iso, usr_tolerance):
    """Correction of high resolution MS data.

    This test is designed to evaluate the correction of high-resolution MS data
    where none of the isotopic species are resolved from the tracer isotopologues,
    i.e. the high-resolution correction algorithm should provides the same correction
    matrix as the one computed using the low-resolution correction algorithm.
    """
    # perform correction
    metabolite = hrcor.HighResMetaboliteCorrector(data["formula"], data["tracer"],
                                                  data_isotopes=data_iso,
                                                  resolution_formula_code="orbitrap",
                                                  correct_NA_tracer=data["correct_NA_tracer"],
                                                  tracer_purity=data["tracer_purity"],
                                                  resolution=data["resolution"],
                                                  mz_of_resolution=data["mz_of_resolution"],
                                                  derivative_formula=data["derivative_formula"],
                                                  charge=1)
    correction_matrix = metabolite.compute_correction_matrix()
    # Test against expected matrix
    p1H = data_iso["H"]["abundance"][0]
    p2H = data_iso["H"]["abundance"][1]
    p12C = data_iso["C"]["abundance"][0]
    p13C = data_iso["C"]["abundance"][1]
    p14N = data_iso["N"]["abundance"][0]
    p15N = data_iso["N"]["abundance"][1]
    p16O = data_iso["O"]["abundance"][0]
    p17O = data_iso["O"]["abundance"][1]
    p18O = data_iso["O"]["abundance"][2]
    pur_12C = data["tracer_purity"][0]
    pur_13C = data["tracer_purity"][1]
    pur1H = data["tracer_purity"][0]
    pur2H = data["tracer_purity"][1]
    expected_matrix = eval(data["expected_matrix"])
    # Low resolution correction matrix
    LRmetabolite = hrcor.LowResMetaboliteCorrector(data["formula"], data["tracer"],
                                                   data_isotopes=data_iso,
                                                   correct_NA_tracer=data["correct_NA_tracer"],
                                                   tracer_purity=data["tracer_purity"],
                                                   derivative_formula=data["derivative_formula"])
    LRcorrection_matrix = LRmetabolite.compute_correction_matrix()
    # Test for equality
    np.testing.assert_allclose(
        correction_matrix, expected_matrix, rtol=usr_tolerance)
    np.testing.assert_allclose(
        correction_matrix, LRcorrection_matrix, rtol=usr_tolerance)
