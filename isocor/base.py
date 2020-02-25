"""Parent classes used by IsoCor to define specific *correctors* sub-classes.

There should be no need to instanciate any of those classes directly.
However, all *correctors* classes should inherit from the classes:

    * :py:class:`~LabelledChemical` that stores data related to the metabolite
      to correct and checks the inputs,
    * :py:class:`~InterfaceMSCorrector` that contractualize what any corrector should be able to do.
"""

import re
import collections
import math
from decimal import Decimal as D


class LabelledChemical(object):
    """A labeled chemical considered for isotope correction.

    This class defines and check the parameters (formulas, tracer, etc.). needed
    to model a chemical undergoing MS correction.

    Default isotopic data come from:

        Isotopic Compositions of the Elements 2013, Pure Appl. Chem.,
        2016, Vol. 88, No. 3, pp. 293-306, https://doi.org/10.1515/pac-2015-0503

    Warning:
        Except specified otherwise, you should never set any attribute at runtime.
        Always make a new instance if you wish to change the parameters.

    Args:
        formula (str): elemental formula of the metabolite moiety (e.g. "C3H7O6P")
        inchi (str): InChI of the metabolite (e.g. "InChI=1/C6H12O6/c7-1-2-3(8)4(9)5(10)6(11)12-2/
            h2-11H,1H2/t2-,3-,4+,5-,6+/m1/s1" for alpha- D -glucopyranose).
            Note that the InChI might represents the metabolite moiety (e.g. a fragment
            ion) or the metabolite, hence its formula may differ from :py:attr:`~formula`.
        tracer (str): the isotopic tracer (e.g. "13C")
        charge (int): charge of the detected ion
        label (str): metabolite abbreviation (e.g. "G3P")
        data_isotopes (dict): isotopic data with mass and abundance
            as in :py:attr:`~LabelledChemical.DEFAULT_ISODATA`.
            If set to `None`, default isotopic data are used.
        derivative_formula (str): elemental formula of the derivative moiety
        tracer_purity (list): proportion of each isotope of the tracer element (metabolite moiety)
            The list must have the same length as the list of isotopes for the relevant
            isotope in :py:attr:`~data_isotopes`. Must be normalized to one.
            If set to `None`, a perfect purity is assumed.
        correct_NA_tracer (bool): flag to correct tracer natural abundance or not.
            If set to True, tracer elements of the metabolite moiety will be
            corrected for the natural isotopic abundance of the tracer.
            Note that tracer elements from the derivative moiety will always be
            corrected at natural abundance (by definition of a derivative moiety).
    """

    DEFAULT_ISODATA = {"C": {"abundance": [0.9893, 0.0107],
                             "mass": [D('12.0'), D('13.003354835')]},
                       "H": {"abundance": [0.999885, 0.000115],
                             "mass": [D('1.0078250322'), D('2.0141017781')]},
                       "N": {"abundance": [0.99636, 0.00364],
                             "mass": [D('14.003074004'), D('15.000108899')]},
                       "P": {"abundance": [1.],
                             "mass": [D('30.973761998')]},
                       "O": {"abundance": [0.99757, 0.00038, 0.00205],
                             "mass": [D('15.99491462'), D('16.999131757'), D('17.999159613')]},
                       "S": {"abundance": [0.9499, 0.0075, 0.0425, 0.0, 0.0001],
                             "mass": [D('31.972071174'), D('32.971458910'), D('33.9678670'), D('35.0'), D('35.967081')]},
                       "Si": {"abundance": [0.92223, 0.04685, 0.03092],
                              "mass": [D('27.976926535'), D('28.976494665'), D('29.9737701')]}}

    def __init__(self, formula, tracer, derivative_formula, tracer_purity,
                 correct_NA_tracer, data_isotopes, charge=None, label=None, inchi=None):
        """Initialize a new LabelledChemical with its associated data."""
        # Load data_isotope first as it is critical for the other attributes
        self._data_isotopes = self.DEFAULT_ISODATA if data_isotopes is None else data_isotopes
        self._check_data_isotopes(self._data_isotopes)
        # Pseudo-private attributes (mostly to work with properties)
        self._molecular_weight = None
        self._tracer_purity = tracer_purity
        self._correct_NA_tracer = correct_NA_tracer
        self._formula = None
        self._inchi = inchi if inchi is not None else ""
        self._isotopic_inchi = None
        self._derivative_formula = None
        self._correction_formula = None
        self._mzshift_tracer = None
        self._str_formula = formula
        self._str_derivative_formula = derivative_formula if derivative_formula is not None else ""
        self._str_tracer_code = tracer
        try:
            self._charge = None if charge is None else abs(int(charge))
            if self._charge == 0:
                raise ValueError(
                    "'charge' parameter should not be 0 ({})".format(charge))
        except:
            raise ValueError("'charge' parameter should be a non-null integer ({})".format(charge))
        # Protected attributes (user should not see them, but must stay available in sub-class)
        self._tracer_el, self._idx_tracer = self._parse_strtracer(
            self._str_tracer_code)
        # Public attributes that could be modified at runtime (not safe)
        # NB: self.data_isotopes is in this category
        self.label = label if label is not None else "|".join([self._str_formula,
                                                               self._str_derivative_formula,
                                                               self._str_tracer_code])
        # Check a few things
        # NB: in the future those checks should be in the setters
        if len(self.data_isotopes[self._tracer_el]["mass"]) != len(self.tracer_purity):
            raise ValueError("Unexpected length of tracer purity vector.")
        if not self.formula:
            raise ValueError("The elemental formula ({}) is empty.".format(self.label))
        if self._tracer_el not in self.formula:
            raise ValueError("The isotopic tracer ({}) must be present in the"
                             " metabolite {}.".format(self._tracer_el, self._str_formula))

    @property
    def data_isotopes(self):
        """dict of dicts: isotopic data with mass and abundance

        See :py:attr:`~LabelledChemical.DEFAULT_ISODATA` for an example.
        """
        return self._data_isotopes

    @property
    def formula(self):
        """Counter: elemental formula of the metabolite moiety"""
        if self._formula is None:
            self._formula = self._parse_strformula(self._str_formula)
        return self._formula

    @property
    def isotopic_inchi(self):
        """Generate isotopic inchis of the corrected fractions, or just the isotopic layer if no
        InChI has been provided.

        Standard proposed by the InChI Isotopologue and Isotopomer Development Team:

        Simple Definition: /a(Ee#<+|->#...)
        Complete Definition:
            /a(<element><isotope_count><isotope_designation>[,<atom_number>])
            <element> - one or two letter Element code (Ee).
            <isotope_count> - number of atoms with the designated isotope (#).
            <isotope_designation> - isotope designation indicated by a sign (+ or -) and number
                indicating the unit mass difference from the rounded average atomic mass of the
                element. For example, the average atomic mass of Sn (118.710) is rounded to 119.
                We specify two 118 Sn atoms as “/a(Sn2-1)”.
        Example: 
            13C2 isotopologue of alpha-D-glucopyranose:
            InChI=1/C6H12O6/c7-1-2-3(8)4(9)5(10)6(11)12-2/h2-11H,1H2/t2-,3-,4+,5-,6+/m1/s1 /a(C2+1),(C4+0)

        Returns:
            list: isotopic inchis
        """
        if self._isotopic_inchi is None:
            tracer_info = self.data_isotopes[self._tracer_el]
            average_iso_mass = round(sum([D(tracer_info["abundance"][i]) * tracer_info["mass"][i] for i in range(len(tracer_info["abundance"]))]))
            tracer_mass = tracer_info["mass"][self._idx_tracer]
            tracer_isotope_designation = round(tracer_mass - average_iso_mass)
            isotope_designation_0 = round(tracer_info["mass"][0] - average_iso_mass)
            # generate isotopic inchis
            self._isotopic_inchi = []
            for j in range(self.formula[self._tracer_el] + 1):
                if j == 0:
                    tmp = '{}/a({}{}{:+d})'.format(self._inchi, self._tracer_el, self.formula[self._tracer_el], isotope_designation_0)
                elif j == self.formula[self._tracer_el]:
                    tmp = '{}/a({}{}{:+d})'.format(self._inchi, self._tracer_el, self.formula[self._tracer_el], tracer_isotope_designation)
                else:
                    tmp = '{}/a({}{}{:+d}),({}{}{:+d})'.format(self._inchi, self._tracer_el, j, tracer_isotope_designation, self._tracer_el, self.formula[self._tracer_el] - j, isotope_designation_0)
                self._isotopic_inchi.append(tmp)
        return self._isotopic_inchi

    @property
    def derivative_formula(self):
        """Counter: elemental formula of the derivative moiety."""
        if self._derivative_formula is None:
            self._derivative_formula = self._parse_strformula(
                self._str_derivative_formula)
        return self._derivative_formula

    @property
    def charge(self):
        """int: absolute value of the charge of the metabolite."""
        return self._charge

    @property
    def inchi(self):
        """str: inchi of the metabolite."""
        return self._inchi

    @property
    def tracer_purity(self):
        """list: proportion of each isotope for the tracer element of the metabolite"""
        if self._tracer_purity is None:  # silently replace None by default value
            default_purity = [0.0] * \
                len(self.data_isotopes[self._tracer_el]["mass"])
            default_purity[self._idx_tracer] = 1.0  # perfect purity
            self._tracer_purity = default_purity
        return self._tracer_purity

    @property
    def correct_NA_tracer(self):
        """bool: correct tracer natural abundance if set to True"""
        return self._correct_NA_tracer

    @property
    def molecular_weight(self):
        """Decimal: exact molecular weight of the metabolite.

        Including the derivative and the tracer.
        """
        if self._molecular_weight is None:
            tmp = [n*self.data_isotopes[el]["mass"][0]
                   for el, n in self.formula.items()]
            if self._str_derivative_formula is not None:
                tmp += [n*self.data_isotopes[el]["mass"][0]
                        for el, n in self.derivative_formula.items()]
            self._molecular_weight = sum(tmp)
        return self._molecular_weight

    @property
    def mzshift_tracer(self):
        """Decimal: mass shift of the tracer

        Warning:
            Mass shift is computed from the first isotope of the list in :py:attr:`~data_isotopes`.
        """
        if self._mzshift_tracer is None:
            tracer_mass = self.data_isotopes[self._tracer_el]["mass"][self._idx_tracer]
            m0_mass = self.data_isotopes[self._tracer_el]["mass"][0]
            self._mzshift_tracer = tracer_mass - m0_mass
            assert self._mzshift_tracer > 0, "Unexpected negative tracer mass shift: {}".format(
                self._mzshift_tracer)
        return self._mzshift_tracer

    @property
    def correction_formula(self):
        """Counter: molecular formula on which the correction will be applied

        This formula is the one on which the correction vector is based.
        Remember that for the correction vector we need **non-tracers atoms**
        from the measured metabolite (all elements excluding the tracer element)
        and **all atoms** from the derivative (including the tracer element).
        """
        if self._correction_formula is None:
            self._correction_formula = {}
            for element, n_atoms in self.formula.items():
                if element != self._tracer_el:
                    self._correction_formula[element] = n_atoms
            if self.derivative_formula is not None:
                for element, n_atoms in self.derivative_formula.items():
                    self._correction_formula[element] = self._correction_formula.get(
                        element, 0) + n_atoms
        return self._correction_formula

    @staticmethod
    def _parse_strformula(str_formula):
        """Parse the molecular formula.

        Args:
            str_formula (str): molecular formula (e.g. "H2O").

        Returns:
            dict: the number of each element in a dictionnary-like
                counter (e.g. {'H':2,'O':1}).
        """
        if str_formula is None:
            return None
        pformula = re.findall(r'([A-Z][a-z]*)(\d*)', str_formula)
        counter = collections.Counter()
        for element, cnt in pformula:
            if cnt == '':
                cnt = 1
            counter[element] += int(cnt)
        return counter

    def _parse_strtracer(self, str_tracer):
        """Parse the tracer code.

        Args:
            str_tracer (str): tracer code (e.g. "13C")

        Returns:
            tuple
                - (str) tracer element (e.g. "C")
                - (int) tracer index in :py:attr:`~data_isotopes`
        """
        try:
            tracer = re.search(r'(\d*)([A-Z][a-z]*)', str_tracer)
            count = int(tracer.group(1))
            tracer_el = tracer.group(2)
        except (ValueError, AttributeError):
            raise ValueError("Invalid tracer code: '{}'."
                             " Please check your inputs.".format(str_tracer))
        best_diff = float("inf")
        idx_tracer = None
        unexpected_msg = "Unexpected tracer code. Are you sure this isotope is "\
                         "in data_isotopes? '{}'".format(str_tracer)
        assert tracer_el in self.data_isotopes, unexpected_msg
        for i, mass in enumerate(self.data_isotopes[tracer_el]["mass"]):
            test_diff = abs(mass - count)
            if test_diff < best_diff:
                best_diff = test_diff
                idx_tracer = i
        assert best_diff < 0.5, unexpected_msg
        return (tracer_el, idx_tracer)

    @staticmethod
    def _check_data_isotopes(data_isotopes):
        """Check :py:attr:`~data_isotopes` validity

        Raises:
            ValueError: :py:attr:`~data_isotopes` is corrupted in some way.
        """
        tol_isomass = 1.2  # arbitrary max mass allowed between two isotope masses (in u)
        for element, data_el in data_isotopes.items():
            if "mass" not in data_el or "abundance" not in data_el:
                raise ValueError(
                    "Invalid data_isotopes. Please check your inputs.")
            if len(data_el["mass"]) != len(data_el["abundance"]):
                raise ValueError("There should ALWAYS be the same number of"
                                 " isotopes mass and abundance in data_isotopes."
                                 " This is not the case for {}.".format(element))
            # Mass specific checks
            if sorted(data_el["mass"]) != data_el["mass"]:
                raise ValueError("Isotopes masses in data_isotopes should"
                                 " ALWAYS be in increasing number. This is not"
                                 " the case for {}.".format(element))
            previous_mass = None
            for mass in data_el["mass"]:
                if previous_mass and mass - previous_mass > tol_isomass:
                    raise ValueError("It seems that data_isotopes is incomplete"
                                     " and that we are missing data for an isotope"
                                     " between masses {} Da and {} Da"
                                     " for {}.".format(previous_mass, mass, element))
                if mass <= 0:
                    raise ValueError("One or several masses are negatives in"
                                     " data_isotopes for element {}.".format(element))
                previous_mass = mass
            # Abundance specific checks
            if math.fsum(data_el["abundance"]) != 1.:
                raise ValueError("The sum of the natural abundance of each isotope"
                                 " should ALWAYS equal 1."
                                 " This is not the case for {}.".format(element))
            for abundance in data_el["abundance"]:
                if not (0. <= abundance <= 1.):
                    raise ValueError("One or several natural abundance are invalid"
                                     " probabilities for isotopic data object for element"
                                     " {}.".format(element))


class InterfaceMSCorrector(object):
    """Interface for Mass Spectrometry correctors.

    This class defines the minimal methods that a corrector should implement.
    Keep in mind that a corrector must inherit from both :py:class:`~InterfaceMSCorrector`
    and :py:class:`~LabelledChemical`.
    """

    class ImproperUsageError(Exception):
        """Raised when the corrector is used incorrectly."""
        pass

    def __init__(self):
        self._correction_matrix = None

    @property
    def correction_matrix(self):
        """Correction matrix.

        The correction matrix will be set once and for all using
        :py:meth:`~compute_correction_matrix` during the first access.
        Use `del x.correction_matrix` if you wish to reset it.
        """
        if self._correction_matrix is None:
            self._correction_matrix = self.compute_correction_matrix()
        return self._correction_matrix

    @correction_matrix.deleter
    def correction_matrix(self):
        self._correction_matrix = None

    def compute_correction_matrix(self):
        """Returns the correction matrix taking into account all parameters.

        Warning:
            Does not set :py:attr:`~correction_matrix` if called directly.

        Returns:
            array: the correction matrix
        """
        raise NotImplementedError(
            "This method must be overloaded in a child class.")

    def correct(self, measurement):
        """Return corrected measurement vector.

        Args:
            measurement (list): measured areas

        Returns:
            tuple:
                - corrected_area (array): Corrected area for each peak.
                - isotopologue_fraction (list): The abundance of each tracer
                  isotopologue (corrected area normalized to 1).
                - residuum
                - mean enrichment
        """
        raise NotImplementedError(
            "This method must be overloaded in a child class.")
