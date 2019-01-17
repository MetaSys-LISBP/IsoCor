"""Test high-resolution correction matrix when some or all isotopic species are resolved from the tracer isotopologues.

In this situation, the contribution of only some isotopic species should be removed,
depending on the resolution.
The high-resolution correction matrix calculated by IsoCor is compared to a theoretical correction matrix
(with algebraic equations provided in the code for manual check).
"""

import numpy as np
import pytest
import isocor as hrcor

# Test the correction matrix by comparison with theoretical matrices expressed using explicit functions (here pXY represents natural
# abundance of isotope X of element Y), which can be easily verified. The examples provided are simple enough for manual verification,
# yet they represent the many situations that can be encountered in the real world. Each situation is detailed in the field "comment".

# Test construction of the correction matrix at high resolution
# tests below are designed to evaluate the correction of high-resolution MS data where some isotopic species are resolved from the tracer-isotopologues


@pytest.mark.parametrize("data", [{"comment": "13C tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 3 isotopes, 17O and 18O are resolved",
                                   "formula": "C2O2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p16O**2, 0.0, 0.0], [0.0, p16O**2, 0.0], [0.0, 0.0, p16O**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2, 0.0, 0.0], [0.0, p1H**2, 0.0], [0.0, 0.0, p1H**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, with NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": True,
                                   "expected_matrix": "[[p1H**2*p12C**2, 0.0, 0.0], [2*p12C*p13C*p1H**2, p1H**2*p12C, 0.0], [p1H**2*p13C**2, p1H**2*p13C, p1H**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 2 isotopes, correct for NA of 2 elements with 2 isotopes",
                                   "formula": "C2H2N2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2*p14N**2, 0.0, 0.0], [0.0, p1H**2*p14N**2, 0.0], [0.0, 0.0, p1H**2*p14N**2]]",
                                   "tracer_purity": [0.0, 1.0]},
                                  {"comment": "13C tracer, no derivative, no NA of the tracer element, with purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "C2H2P10",
                                   "tracer": "13C",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[p1H**2, p1H**2*pur_12C, p1H**2*pur_12C*pur_12C], [0.0, p1H**2*pur_13C, p1H**2*pur_12C*pur_13C*2], [0.0, 0.0, p1H**2*pur_13C*pur_13C]]",
                                   "tracer_purity": [0.1, 0.9]},
                                  # tests for tracers having more than 2 isotopes
                                  {"comment": "17O tracer, no derivative, no NA of the tracer element, with purity of the tracer element, tracer with 2 isotopes, correct for NA of 1 elements with 2 isotopes",
                                   "formula": "O",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": True,
                                   "expected_matrix": "[[p16O, 0.0], [p17O, 0.0]]",
                                   "tracer_purity": [0.0, 0.0, 1.0]},
                                  {"comment": "17O tracer, no derivative, NA of the tracer element, no purity of the tracer element, tracer with 3 isotopes, correct for NA of 0 elements",
                                   "formula": "O",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": True,
                                   "expected_matrix": "[[p16O, 0.0], [p17O, 1.0]]",
                                   "tracer_purity": [0.0, 1.0, 0.0]},
                                  {"comment": "17O tracer, no derivative, no NA of the tracer element, no purity of the tracer element, tracer with 3 isotopes, correct for NA of 0 elements",
                                   "formula": "O1",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[1.0, 0.0], [0.0, 1.0]]",
                                   "tracer_purity": [0.0, 1.0, 0.0]},
                                  {"comment": "17O tracer, no derivative, no NA of the tracer element, with purity of the tracer element, tracer with 3 isotopes, correct for NA of 0 elements",
                                   "formula": "O1",
                                   "tracer": "17O",
                                   "derivative_formula": "",
                                   "resolution": 1e6,
                                   "mz_of_resolution": 400,
                                   "correct_NA_tracer": False,
                                   "expected_matrix": "[[1.0, 0.1], [0.0, 0.9]]",
                                   "tracer_purity": [0.1, 0.9, 0.0]}])
def test_high_res_cor_matrix(data, data_iso, usr_tolerance):
    """Correction of high-resolution MS data.

    Test calculates the correction matrix of labeled metabolites containing C, H, N and O elements,
    and compares this matrix to a theoretical matrix.
    """
    # perform correction
    metabolite = hrcor.HighResMetaboliteCorrector(data["formula"], data["tracer"],
                                                  data_isotopes=data_iso,
                                                  correct_NA_tracer=data["correct_NA_tracer"],
                                                  resolution_formula_code = "orbitrap",
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
    np.testing.assert_allclose(
        correction_matrix, expected_matrix, rtol=usr_tolerance)
