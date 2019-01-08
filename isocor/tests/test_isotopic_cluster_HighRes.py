"""Test the calculation of high-resolution isotopic clusters (for metabolites with
different number of elements and isotopes) against a brute force implementation.
"""

import math
import itertools as it
import pytest
import numpy as np
import isocor as hrcor


def get_isoclust_bruteforce(formula, data_iso):
    """Return the isotopic cluster for a compound using a brute-force method.

    This method is based on systematic computation of all isotopic species of the molecule.
    It should be easier to understand than the optimized version but is much slower.
    """
    def npermutations(v):
        dem = 1
        for x in set(v):
            dem *= math.factorial(v.count(x))
        return math.factorial(len(v)) / dem
    isotopic_cluster = {}  # {isotopologue_mass: isotopologue_proba, ...}
    # For each element, gather the possible combinations of its isotopes
    element_blocks = []   # list of iterators over isotopes combinations for one element
    elements_order = []  # e.g.: ["C", "N", "H"] states thats "C" block is at index 0
    for element in formula:
        # number of natural isotopes
        n_isotopes = len(data_iso[element]["mass"])
        iter_iso_combi = it.combinations_with_replacement(range(n_isotopes),  # allowed isotopes (index of data_iso)
                                                          formula[element])   # number of this element in formula
        elements_order.append(element)
        element_blocks.append(iter_iso_combi)
    # Make an iterator over all isotopologues
    # NB: simply take one combination/block for each element
    iter_isotopologues = it.product(*element_blocks)
    # Process each isotopologue
    for isotopologue in iter_isotopologues:
        # Compute the mass of the isotopologue
        mass_by_block = []
        for idx_element, combi_isotopes in enumerate(isotopologue):
            element = elements_order[idx_element]
            isotope_mass = [data_iso[element]["mass"][idx_iso]
                            for idx_iso in combi_isotopes]
            mass_by_block.append(sum(isotope_mass))
        mass_isotopologue = sum(mass_by_block)
        # Compute the expected abundance for this isotopologue
        n_isotopomers_by_block = []  # number of isotopomers caused by each element_block
        listof_block_proba = []      # proba of each element_block
        for idx_element, combi_isotopes in enumerate(isotopologue):
            n_isotopomers_by_block.append(npermutations(combi_isotopes))
            element = elements_order[idx_element]  # e.g. "C"
            block_proba = np.prod(
                [data_iso[element]["abundance"][idx_iso] for idx_iso in combi_isotopes])
            listof_block_proba.append(block_proba)
        proba_isotopologue = np.prod(
            n_isotopomers_by_block) * np.prod(listof_block_proba)
        # Save
        assert mass_isotopologue not in isotopic_cluster
        isotopic_cluster[mass_isotopologue] = proba_isotopologue
    return isotopic_cluster


@pytest.mark.parametrize("formula", [{"C": 1, "N": 1},
                                     {"C": 1, "O": 1},
                                     {"C": 1, "N": 2},
                                     {"C": 1, "O": 2},
                                     {"C": 1, "N": 20, "H": 20, "O": 20, "P": 4},
                                     {"C": 20, "N": 20, "H": 20, "O": 20, "P": 4}])
def test_isoclust_against_bruteforce(formula, data_iso, usr_tolerance):
    """Check the high-resolution isotopic clusters generation against a brute force implementation."""
    str_formula = "".join(["{}{}".format(k, v) for k, v in formula.items()])
    # Get the clusters (without tracers)
    try:
        del formula["C"]
    except:
        pass
    ic_bruteforce = get_isoclust_bruteforce(formula, data_iso)
    metabolite = hrcor.HighResMetaboliteCorrector(str_formula, '13C', 1e42, 400,
                                                  resolution_formula_code="orbitrap",
                                                  derivative_formula=None,
                                                  tracer_purity=None,
                                                  data_isotopes=data_iso,
                                                  correct_NA_tracer=False,
                                                  charge=1)
    metabolite.threshold_p = None
    ic_optimized = metabolite.get_isotopic_cluster()
    # Check that all isotopomeres are taken into account
    np.testing.assert_allclose(
        sum(ic_bruteforce.values()), 1., rtol=usr_tolerance)
    np.testing.assert_allclose(
        sum(ic_optimized.values()), 1., rtol=usr_tolerance)
    # Check that both methods have the same number of isotopologues
    assert len(ic_bruteforce) == len(ic_optimized)
    # Finally, check each mass (key) and each abundance (value)
    mass_optimized = [float(x) for x in sorted(ic_optimized.keys())]
    mass_bruteforce = [float(x) for x in sorted(ic_bruteforce.keys())]
    np.testing.assert_allclose(
        mass_optimized, mass_bruteforce, rtol=usr_tolerance)
    abun_optimized = [float(x) for x in sorted(ic_optimized.values())]
    abun_bruteforce = [float(x) for x in sorted(ic_bruteforce.values())]
    np.testing.assert_allclose(
        abun_optimized, abun_bruteforce, rtol=usr_tolerance)
