"""Test the MetaboliteCorrectorFactory."""

import pytest
import isocor as hrcor


def test_MetaboliteCorrectorFactory(data_iso):
    """Test that the Factory can be instanciated safely."""
    # Low resolution
    x = hrcor.MetaboliteCorrectorFactory(
        "C3H7O6P", '13C', data_isotopes=data_iso)
    assert isinstance(x, hrcor.mscorrectors.LowResMetaboliteCorrector)
    # High resolution
    x = hrcor.MetaboliteCorrectorFactory("C3H7O6P", '13C', data_isotopes=data_iso,
                                         resolution=1e4, mz_of_resolution=400, charge=1)
    assert isinstance(x, hrcor.mscorrectors.HighResMetaboliteCorrector)


@pytest.mark.parametrize("bad_dataiso", [{'C': {}},
                                         {'C': {'masses': [], 'abundance': []}},
                                         {'C': {'mass': [12, 13],
                                                'abundance': [1.]}},
                                         {'C': {'mass': [12, 13],
                                                'abundance': [1., 1.]}},
                                         {'C': {'mass': [12, 14], 'abundance': [.5, .5]}}])
def test_isotopedata(bad_dataiso):
    """Tests expected to fail because of a badly formatted data_isotopes."""
    with pytest.raises(ValueError):
        hrcor.MetaboliteCorrectorFactory("C", '13C', data_isotopes=bad_dataiso)

def test_typo_factory(data_iso):
    """Test a typo in the name of one of the parameters (Factory)."""
    with pytest.raises(ValueError):
        hrcor.MetaboliteCorrectorFactory("C3PO", "13C",
                                         wrong_data_isotopes_parameter=data_iso,
                                         correct_NA_tracer=False,
                                         derivative_formula=None,
                                         tracer_purity=None)

def test_typo_parameter(data_iso):
    """Test a typo in the name of one of the parameters (LowRes)."""
    with pytest.raises(TypeError):
        hrcor.LowResMetaboliteCorrector("C3PO", "13C",
                                        wrong_data_isotopes_parameter=data_iso,
                                        correct_NA_tracer=False,
                                        derivative_formula=None,
                                        tracer_purity=None)

@pytest.mark.parametrize("kwargs", [
    {"formula":"C", "tracer":'13C', "data_isotopes":None,
     "resolution":"42o", "mz_of_resolution":420},
    {"formula":"C", "tracer":'13C', "data_isotopes":None,
     "resolution":"420", "mz_of_resolution":"42o"}
])
def test_badinput(kwargs, data_iso):
    """Test a wrong type of parameter value (Factory)."""
    kwargs["data_isotopes"] = data_iso
    with pytest.raises(ValueError):
        hrcor.MetaboliteCorrectorFactory(**kwargs)
