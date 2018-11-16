"""Test the calculation of low-resolution isotopic clusters (for metabolites with
different number of elements and isotopes) against a brute force implementation.
"""

import pytest
import numpy as np
import isocor as hrcor


def get_isoclust_bruteforce(formula, data_iso):
    """Return the low-resolution isotopic cluster of a compound using convolution."""
    result = [
        1.]  # mass are normalized to 1; also default value if no correction_formula
    for el, n in formula.items():
        for _ in range(n):
            result = np.convolve(result, data_iso[el]["abundance"])
    return list(result)


@pytest.mark.parametrize("formula", [{"C": 1, "N": 1},
                                     {"C": 1, "O": 1},
                                     {"C": 1, "N": 2},
                                     {"C": 1, "O": 2},
                                     {"C": 1, "N": 20, "H": 20, "O": 20, "P": 4},
                                     {"C": 20, "N": 20, "H": 20, "O": 20, "P": 4}])
def test_isoclust_against_bruteforce(formula, data_iso, usr_tolerance):
    """Check the low resolution isotopic clusters generation against a simple implementation."""
    str_formula = "".join(["{}{}".format(k, v) for k, v in formula.items()])
    # Get the clusters (without tracers)
    del formula["C"]
    ic_bruteforce = get_isoclust_bruteforce(formula, data_iso)
    metabolite = hrcor.LowResMetaboliteCorrector(str_formula, '13C',
                                                 data_isotopes=data_iso,
                                                 derivative_formula=None,
                                                 tracer_purity=None,
                                                 correct_NA_tracer=False)
    ic_optimized = metabolite.get_mass_distribution_vector()
    # Check that all isotopomeres are taken into account
    np.testing.assert_allclose(sum(ic_bruteforce), 1., rtol=usr_tolerance)
    np.testing.assert_allclose(sum(ic_optimized), 1., rtol=usr_tolerance)
    # Check that both methods have the same number of isotopologues
    assert len(ic_bruteforce) == len(ic_optimized)
    # Finally, check each abundance
    np.testing.assert_allclose(ic_bruteforce, ic_optimized, rtol=usr_tolerance)
