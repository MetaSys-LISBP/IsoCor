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
                                         resolution=1e4, mz_of_resolution=400)
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
