"""*Correctors* classes of IsoCor for mass spectrometry data.

Metabolite *correctors* are metabolite-centered objects used to correct
mass spectrometry data for natural abundance and tracer purity.

Metabolite *correctors* can be instanciated directly or through their factory (recommended).
"""

import math
import functools
import itertools as it
import logging
from decimal import Decimal as D
import numpy as np
from scipy.optimize import fmin_l_bfgs_b
from isocor.base import LabelledChemical, InterfaceMSCorrector

logger = logging.getLogger(__name__)


class MetaboliteCorrectorFactory(object):
    """A Factory that returns the right *metabolite corrector* given the correction options.

    Args:
        formula (str): elemental formula of the metabolite moiety (e.g. "C3H7O6P")
        inchi (str): InChI of the metabolite (e.g. "InChI=1/C6H12O6/c7-1-2-3(8)4(9)5(10)6(11)12-2/
            h2-11H,1H2/t2-,3-,4+,5-,6+/m1/s1" for alpha- D -glucopyranose).
            Note that the InChI might represents the metabolite moiety (e.g. a fragment
            ion) or the metabolite, hence its formula may differ from :py:attr:`~formula`.
        tracer (str): the isotopic tracer (e.g. "13C")
        label (str): metabolite abbreviation (e.g. "G3P")
        data_isotopes (dict): isotopic data with mass and abundance
            as in :py:attr:`~LabelledChemical.DEFAULT_ISODATA` (default values)
        derivative_formula (str): elemental formula of the derivative moiety (default:
            no derivative)
        tracer_purity (list): proportion of each isotope of the tracer element (metabolite moiety)
            The list must have the same length as the list of isotopes for the relevant
            isotope in :py:attr:`~data_isotopes`. Must be normalized to one.
            Default is perfect purity.
        correct_NA_tracer (bool): flag to correct tracer natural abundance or not.
            If set to True, tracer elements of the metabolite moiety will be
            corrected for the natural isotopic abundance of the tracer.
            Note that tracer elements from the derivative moiety will always be
            corrected at natural abundance (by definition of a derivative moiety).
            Default is False.
        resolution (int): resolution of the mass spectrometer (e.g. "1e4");
            default "None" (low-resolution).
        mz_of_resolution (int): m/z at which the resolution was measured (e.g. "400").
            This is **not** the m/z of the metabolite.
        resolution_formula_code (str): code for the resolution formula you wish to use to compute
            the correction limit among the presets: "orbitrap" (default), "ft-icr", and "constant".
            This formula depends on your mass spectrometer.
        charge (int): charge state of the metabolite (e.g. "-2").

    Raises:
        ValueError: wrong input
        ImproperUsageError: incoherent input
    """
    def __new__(cls, formula, tracer, **kwargs):
        corrector = None
        # Gather common parameters and set default values
        label = kwargs.pop("label", None)
        inchi = kwargs.pop("inchi", None)
        data_isotopes = kwargs.pop("data_isotopes", None)
        derivative_formula = kwargs.pop("derivative_formula", None)
        tracer_purity = kwargs.pop("tracer_purity", None)
        correct_NA_tracer = kwargs.pop("correct_NA_tracer", False)
        # Gather up parameters used for specific correctors
        resolution = kwargs.pop("resolution", None)
        charge = kwargs.pop("charge", None)
        mz_of_resolution = kwargs.pop("mz_of_resolution", None)
        resolution_formula_code = kwargs.pop("resolution_formula_code", "orbitrap")
        # Choose a corrector
        if resolution is None and mz_of_resolution is None:
            logger.debug("MetaboliteCorrectorFactory chose to use a"
                         " LowResMetaboliteCorrector for %s.", formula)
            corrector = LowResMetaboliteCorrector(formula, tracer, label=label,
                                                  data_isotopes=data_isotopes,
                                                  derivative_formula=derivative_formula,
                                                  tracer_purity=tracer_purity,
                                                  correct_NA_tracer=correct_NA_tracer,
                                                  inchi=inchi)
        elif resolution and mz_of_resolution and charge:
            logger.debug("MetaboliteCorrectorFactory chose to use a"
                         " HighResMetaboliteCorrector for %s.", formula)
            try:
                corrector = HighResMetaboliteCorrector(formula, tracer, resolution, mz_of_resolution,
                                                       label=label,
                                                       data_isotopes=data_isotopes,
                                                       derivative_formula=derivative_formula,
                                                       tracer_purity=tracer_purity,
                                                       correct_NA_tracer=correct_NA_tracer,
                                                       resolution_formula_code=resolution_formula_code,
                                                       charge=charge,
                                                      inchi=inchi)
            except InterfaceMSCorrector.ImproperUsageError as reason:
                logger.warning("Improper usage of HighResMetaboliteCorrector "
                               "by MetaboliteCorrectorFactory."
                               " Falling back to LowResMetaboliteCorrector."
                               " Reason: %s", reason)
                corrector = LowResMetaboliteCorrector(formula, tracer, label=label,
                                                      data_isotopes=data_isotopes,
                                                      derivative_formula=derivative_formula,
                                                      tracer_purity=tracer_purity,
                                                      correct_NA_tracer=correct_NA_tracer,
                                                      inchi=inchi)
        else:
            message = "MetaboliteCorrectorFactory was unable to select a" \
                      " correction strategy. Please check your inputs."
            logger.error(message)
            raise ValueError(message)
        # Warn user if a parameter some parameters were not utilized
        if kwargs:
            msg = "Unused parameters: {}. Maybe a typo?".format(str(kwargs))
            logger.error(msg)
            raise ValueError(msg)
        return corrector


class LowResMetaboliteCorrector(LabelledChemical, InterfaceMSCorrector):
    """Metabolite *corrector* for low-resolution mass-spectrometry data.

    At low-resolution, all isotopologues with the same nominal mass are
    considered to be measured together.

    Args:
        formula (str): elemental formula of the metabolite moiety (e.g. "C3H7O6P")
        inchi (str): InChI of the metabolite (e.g. "InChI=1/C6H12O6/c7-1-2-3(8)4(9)5(10)6(11)12-2/
            h2-11H,1H2/t2-,3-,4+,5-,6+/m1/s1" for alpha- D -glucopyranose).
            Note that the InChI might represents the metabolite moiety (e.g. a fragment
            ion) or the metabolite, hence its formula may differ from :py:attr:`~formula`.
        tracer (str): the isotopic tracer (e.g. "13C")
        label (str): metabolite abbreviation (e.g. "G3P")
        data_isotopes (dict): isotopic data with mass and abundance
            as in :py:attr:`~LabelledChemical.DEFAULT_ISODATA`
        derivative_formula (str): elemental formula of the derivative moiety
        tracer_purity (list): proportion of each isotope of the tracer element (metabolite moiety)
            The list must have the same length as the list of isotopes for the relevant
            isotope in :py:attr:`~data_isotopes`. Must be normalized to one.
            Default is perfect purity.
        correct_NA_tracer (bool): flag to correct tracer natural abundance or not.
            If set to True, tracer elements of the metabolite moiety will be
            corrected for the natural isotopic abundance of the tracer.
            Note that tracer elements from the derivative moiety will always be
            corrected at natural abundance (by definition of a derivative moiety).
    """

    def __init__(self, formula, tracer, **kwargs):
        LabelledChemical.__init__(self, formula, tracer, **kwargs)
        InterfaceMSCorrector.__init__(self)
        # Log if direct instanciation
        if self.__class__.__name__ == LowResMetaboliteCorrector.__name__:
            self._log_on_init()

    def _log_on_init(self):
        """Log instantiation of a new metabolite corrector object."""
        key_debug_log = ["data_isotopes"]
        logme_info = []
        logme_debug = []
        for k, v in vars(self).items():
            if k not in key_debug_log:
                logme_info.append((k, v))
            else:
                logme_debug.append((k, v))
        logger.debug("New %s, %s: %s.", self.__class__.__name__,
                    self.label, logme_info)
        logger.debug("%s additionally uses: %s", self.label, logme_debug)

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
        logger.debug("New correction for %s with: measurement=%s.",
                     self.label, measurement)
        # Check length
        if len(measurement) != self.formula[self._tracer_el] + 1:
            raise ValueError("The length of the measured isotopic cluster ({}) is different"
                             " than the required number of measurements: {}"
                             " (i.e. N + 1, where N is the number of atoms that could"
                             " be traced)".format(len(measurement),
                                                  self.formula[self._tracer_el] + 1))
        # Perform the actual correction
        corrected_area, iso_fraction, residuum, enrichment = self._correct_with_bfgs(
            measurement)
        logger.debug(
            "Finished correction. Residuum (normalized to 1): %s", residuum)
        return corrected_area, iso_fraction, residuum, enrichment

    @staticmethod
    def _get_cost_function(mid, v_mes, mat_cor):
        """Cost function used for optimization.

        See also scipy.optimize.fmin_l_bfgs_b().

        Args:
            mid: isotopologue_fraction
            v_mes (array): measurement vector
            mat_cor (array): correction matrix

        Returns:
            float: (sum(v_mes - mat_cor * mid)^2, gradient)
        """
        x = v_mes - np.dot(mat_cor, mid)
        # calculate sum of square differences and gradient
        return (np.dot(x, x), np.dot(mat_cor.transpose(), x)*-2)

    def _correct_with_bfgs(self, measurement):
        """Perform the correction of the measurement vector using a L-BFGS-B algorithm.

        Args:
            measurement (list): measurement vector
        """
        # perform correction and calculate residuum
        v_mes = np.array(measurement).transpose()
        length_result = self.formula[self._tracer_el] + 1
        corrected_area, _, _ = fmin_l_bfgs_b(self._get_cost_function,
                                             np.zeros(length_result),
                                             fprime=None,
                                             approx_grad=0,
                                             args=(
                                                 v_mes, self.correction_matrix),
                                             factr=1000,
                                             pgtol=1e-10,
                                             bounds=[(0., float('inf'))] * length_result)
        resi = v_mes - np.dot(self.correction_matrix, corrected_area)
        # normalize mid and residuum
        sum_p = math.fsum(corrected_area)
        if sum_p != 0:
            isotopologue_fraction = [p/sum_p for p in corrected_area]
            enrichment = math.fsum(
                p*i for i, p in enumerate(isotopologue_fraction))/self.formula[self._tracer_el]
        else:
            isotopologue_fraction = [np.NaN for p in corrected_area]
            enrichment = np.NaN
        sum_m = math.fsum(measurement)
        if sum_m != 0:
            residuum = [v/sum_m for v in resi]
        else:
            residuum = [np.NaN for v in resi]
        return corrected_area, isotopologue_fraction, residuum, enrichment

    def get_mass_distribution_vector(self):
        """Get low resolution mass distribution vector (at natural abundance) for non-tracers elements.

        Based on the elemental compositions of both metabolite's and derivative's moieties.
        The element corresponding to the isotopic tracer is ignored.

        Calculation is based on convolution of isotopic vectors of individual elements (IsoCor,
        Millard et al., 2012), which is much faster than the combinatorial approach implemented for
        simulation at high resolution.

        Returns:
            list: mass distribution vector
        """
        result = [1.]  # mass are normalized to 1; also default value if no correction_formula
        for el, n in self.correction_formula.items():
            for _ in range(n):
                result = np.convolve(
                    result, self.data_isotopes[el]["abundance"])
        logger.debug("Done computing mass distribution vector for non-tracers "
                     "elements of %s (convolution method): %s", self.label, result)
        return list(result)

    def _correctionmatrix_convolution(self):
        """Return the correction matrix build with the convolution algorithm.

        Each column is constructed by iterative convolution of the correction vector.

        Returns:
            array: correction_matrix
        """
        correction_vector = self.get_mass_distribution_vector()
        n_isotopologues = self.formula[self._tracer_el] + 1
        # create correction matrix
        correction_matrix = np.zeros((n_isotopologues, n_isotopologues))
        # Peaks to keep after convolution
        mask = [n * self._idx_tracer for n in range(n_isotopologues)]
        # For each atom with the same element as the tracer
        for i in range(n_isotopologues):
            column = correction_vector
            # Correction of tracer purity
            for _ in range(i):
                column = np.convolve(column, self.tracer_purity)
            # Correct natural abundance of tracer element (if relevant)
            if self.correct_NA_tracer:
                for _ in range(n_isotopologues-i-1):
                    column = np.convolve(
                        column, self.data_isotopes[self._tracer_el]["abundance"])
            if len(column) < max(mask)+1:
                column += [0.]*(max(mask)-len(column)+1)
            column = [column[j] for j in mask]
            correction_matrix[:, i] = column
        logger.debug("Done computing correction matrix (convolution) for %s: %s",
                     self.label, correction_matrix.tolist())
        return correction_matrix

    def compute_correction_matrix(self):
        """Returns the correction matrix taking into account all parameters.

        Attention:
            Does not set :py:attr:`~correction_matrix` if called directly.

        Returns:
            array: the correction matrix
        """
        logger.debug("Computing correction matrix for %s...", self.label)
        return self._correctionmatrix_convolution()


class HighResMetaboliteCorrector(LowResMetaboliteCorrector):
    """Metabolite *corrector* for high-resolution mass-spectrometry data.

    At high-resolution, we consider that the measured peak **may not** encompass
    all isotopologues due to isotope natural abundance, depending on the operating
    resolution of the mass spectrometer at a given m/z.

    This is essentially the same correction pipeline as for low-resolution data,
    except that the calculation of the correction vector must be more precise and
    therefore requires a more complex (and more time-consumming) algorithm.

    Args:
        formula (str): elemental formula of the metabolite moiety (e.g. "C3H7O6P")
        tracer (str): the isotopic tracer (e.g. "13C")
        label (str): metabolite abbreviation (e.g. "G3P")
        inchi (str): InChI of the metabolite (e.g. "InChI=1/C6H12O6/c7-1-2-3(8)4(9)5(10)6(11)12-2/
            h2-11H,1H2/t2-,3-,4+,5-,6+/m1/s1" for alpha- D -glucopyranose).
            Note that the InChI might represents the metabolite moiety (e.g. a fragment
            ion) or the metabolite, hence its formula may differ from :py:attr:`~formula`.
        data_isotopes (dict): isotopic data with mass and abundance
            as in :py:attr:`~LabelledChemical.DEFAULT_ISODATA`
        derivative_formula (str): elemental formula of the derivative moiety
        tracer_purity (list): proportion of each isotope of the tracer element (metabolite moiety)
            The list must have the same length as the list of isotopes for the relevant
            isotope in :py:attr:`~data_isotopes`. Must be normalized to one.
        correct_NA_tracer (bool): flag to correct tracer natural abundance or not.
            If set to True, tracer elements of the metabolite moiety will be
            corrected for the natural isotopic abundance of the tracer.
            Note that tracer elements from the derivative moiety will always be
            corrected at natural abundance (by definition of a derivative moiety).
        resolution (int): resolution of the mass spectrometer (e.g. "1e4")
        mz_of_resolution (int): m/z at which the resolution was measured (e.g. "400").
            This is **not** the m/z of the metabolite.
        resolution_formula_code (str): code for the resolution formula you wish to use to compute
            the correction limit among the presets: "orbitrap", "ft-icr", and "constant".
            This formula depends on your mass spectrometer.
        resolution_formula (func): (EXPERIMENTAL) if no code suits you, you
            can use this parameter to provide a function returning the resolution at the mz of the metabolite.
            Use the same format as in :attr:`~RES_FORMULAS`.
            :attr:`~resolution_formula` has precedence over :attr:`~resolution_formula_code`.
        charge (int): charge state of the metabolite (e.g. "-2").
    """
    # Registered resolution formulas to compute local resolution
    # parameters: molecular weight (mw), resolution (res) at mass-to-charge ratio (at_mz)
    RES_FORMULAS = {
        "orbitrap": lambda mw, res, at_mz: 1.66*mw**(3/2)/(res*math.sqrt(at_mz)),
        "ft-icr": lambda mw, res, at_mz: 1.66*mw**2/(res*at_mz),
        "constant": lambda mw, res, at_mz: 1.66*mw/res,
        "datafile": lambda mw, res, at_mz: 1.66*mw/res
    }

    def __init__(self, formula, tracer, resolution, mz_of_resolution, resolution_formula_code, charge, **kwargs):
        LowResMetaboliteCorrector.__init__(self, formula, tracer, charge=charge, **kwargs)
        # Some checks on the inputs
        try:
            resolution = float(resolution)
            mz_of_resolution = float(mz_of_resolution)
        except ValueError as msg:
            raise ValueError("Parameters 'resolution' and 'mz_of_resolution' "
                             "should be numeric: {}".format(msg))
        if resolution <= 0.:
            raise ValueError(
                "'resolution' parameter should be >0 ({})".format(resolution))
        if mz_of_resolution <= 0.:
            raise ValueError(
                "'mz_of_resolution' parameter should be >0 ({})".format(mz_of_resolution))
        try:
            resolution_formula = kwargs.get("resolution_formula",
                                            self.RES_FORMULAS[resolution_formula_code])
        except KeyError:
            raise NotImplementedError("No resolution formula registered for code '{}'. "
                                      "Please provide the formula as resolution_formula"
                                      "parameter.".format(resolution_formula_code))
        # Check correction limit
        self._correction_limit = resolution_formula(float(self.molecular_weight)/self.charge, resolution, mz_of_resolution) * self.charge
        self.threshold_p = None if self.molecular_weight < 500 else 1e-10
        precision_machine = 10**3 * np.finfo(float).eps
        if self.correction_limit >= 0.5:
            raise self.ImproperUsageError("The correction limit is expected to be sufficent"
                                          " to distinguish peaks with a delta-mass of 1 amu"
                                          " ({}>0.5).".format(self.correction_limit))
        elif self.correction_limit < precision_machine:
            logger.warning("Correction limit is close to machine limits for floating point"
                           " operations. Correction limit reset to: %s", precision_machine)
            self._correction_limit = precision_machine
        # Log if direct instantiation
        if self.__class__.__name__ == HighResMetaboliteCorrector.__name__:
            self._log_on_init()

    @property
    def correction_limit(self):
        """Operative correction limit (in Da).

        Depends on the calibration resolution, the m/z at which the instrument
        was calibrated, the m/z of the meabolite and of course the formula that
        gives the relation between those values (that depends on the spectrometer).
        """
        return self._correction_limit

    # @staticmethod
    # def _count_isoblocks(n_isotopes, n_atoms):
    #     return int(math.factorial(n_isotopes+n_atoms-1) / math.factorial(n_atoms) / math.factorial(n_isotopes-1))

    @staticmethod
    def _count_isotopomers(isoblock):
        """Return the number of isotopomers for a given element/isoblock (permutations)."""
        dem = 1
        for x in set(isoblock):
            dem *= math.factorial(isoblock.count(x))
        return int(math.factorial(len(isoblock)) / dem)

    def _get_block_1(self, mass, n_atoms):
        return [(mass * n_atoms, 1.0)]

    def _get_block_2(self, masses, abundances, n_atoms):
        l_p = [1.]
        for i in range(n_atoms):
            l_p = np.convolve(l_p, abundances)
        res = [(masses[0]*(n_atoms-i) + masses[1]*i, l_p[i])
               for i in range(n_atoms+1)]
        return res

    def _get_block_n(self, masses, abundances, n_atoms, n_isotopes):
        all_res = []
        # Given a block of isotopes, fill its mass and proba
        all_isoblocks = it.combinations_with_replacement(
            range(n_isotopes), n_atoms)
        for isoblock in all_isoblocks:
            # Mass of this block
            block_mass = sum([masses[i] for i in isoblock])
            # Probability to see this block
            # NB: corrected by the number of isotopomere confounded in THIS block
            tmp_proba = [abundances[i] for i in isoblock]
            n_isotopomeres = self._count_isotopomers(isoblock)
            block_abundance = n_isotopomeres * \
                functools.reduce(lambda x, y: x*y, tmp_proba)
            all_res.append((block_mass, block_abundance))
        return all_res

    def _get_isotopic_blocks(self):
        """Return all combinations of isotopes by "block" of element."""
        data = {}  # mass and probability of each elemental block given its isotopic composition
        # Work element by element, to make elemental blocks (isotopes combinations)
        for element in self.correction_formula:
            n_isotopes = len(self.data_isotopes[element]["mass"])
            n_atoms = self.correction_formula[element]
            # TODO: check that the performances are improved with the different cases
            if n_isotopes == 1:
                # if element has only 1 isotope, probability is 1.0 by definition
                data[element] = self._get_block_1(
                    self.data_isotopes[element]["mass"][0], n_atoms)
            elif n_isotopes == 2:
                # if element has 2 isotope, use convolution method to calculate its mid
                data[element] = self._get_block_2(self.data_isotopes[element]["mass"],
                                                  self.data_isotopes[element]["abundance"],
                                                  n_atoms)
            else:
                # if element has 3 or more isotope, use full computation
                data[element] = self._get_block_n(self.data_isotopes[element]["mass"],
                                                  self.data_isotopes[element]["abundance"],
                                                  n_atoms, n_isotopes)
            # Keep only the blocks above probability threshold
            # NB: when the different elements are combined, peaks are always
            # multiplied by a number <1, so if any block is < threshold,
            # then the peak will be too
            assert all([x[1] >= 0 for x in data[element]]
                       ), "Unexpected negative probability."
            if self.threshold_p is not None:
                for peak in data[element]:
                    if peak[1] <= self.threshold_p:  # abundance
                        del peak
        return data

    def _combine_blocks(self, groups):
        """Combine blocks of isotopes together and compute the isotopic cluster."""
        def helper(X, Y):
            for x, y in it.product(X, Y):
                yield x[0] + y[0], x[1] * y[1]
        # generator over the data, by element
        g = (groups[element] for element in groups)
        iso_clust = dict()  # {mass: proba, ...}
        for mass, proba in functools.reduce(helper, g):
            if mass not in iso_clust:
                iso_clust[mass] = proba
            else:
                iso_clust[mass] += proba
        # Trim out the peaks below probability
        if self.threshold_p is not None:
            to_del = []
            for k in iso_clust:
                if iso_clust[k] <= self.threshold_p:
                    to_del.append(k)
            for k in to_del:
                del iso_clust[k]
        return iso_clust

    def get_isotopic_cluster(self):
        """Return the full isotopic cluster of the compound (for non-tracer elements).

        Args:
            threshold_p (float): Probability threshold under which a peak will be
                ignored (default: keep all peaks).

        Returns:
            dict: isotopologues masses mapped to their respective expected abundance
            (e.g. `{83.9959772546: 0.966808533640457, ...}`).
        """
        assert self.threshold_p is None or (0 <= self.threshold_p <= 1), \
            "Unexpected probability for 'threshold_p': {}".format(self.threshold_p)
        if self.correction_formula:
            groups = self._get_isotopic_blocks()
            iso_clust = self._combine_blocks(groups)
        else:
            iso_clust = None  # no atom, no isotopic cluster
        return iso_clust

    def get_tracershifted_peaks_between(self, mz_min, mz_max):
        """Return the mass of all the peaks that originate from the tracer.

        Those peaks are the 'main' peaks around which we will find other
        peaks due to the incorporation of natural isotopes of non-tracer elements
        (different from the most abundant isotope).

        Args:
            mz_min (float): minimum range
            mz_max (float): maximum range

        Returns:
            list: mass of all peaks that originate from the tracer
        """
        assert mz_max > mz_min, "Unexpected parameters: {} should be < to {}".format(
            mz_min, mz_max)
        n_peaks = math.floor((mz_max - mz_min)/self.mzshift_tracer) + 1
        id_mass = [mz_min + n * self.mzshift_tracer for n in range(n_peaks)]
        return id_mass

    def get_peaks_around(self, isotopic_cluster, masses):
        """Sum unresolved peaks of isotopic cluster according to the MS resolution.

        Args:
            isotopic_cluster (dict): isotopic cluster as returned by `:meth:~get_isotopic_cluster`
            masses (list): m/z around which peaks will be pooled

        Returns:
            list: abundances for each input mass, after sorting the mass and
            pooling nearby peaks within the resolution limit (:attr:`~correction_limit`)
        """
        # NB: masses are not garanteed to be in isotopic_cluster; if no peak is
        # found nearby, a 0.0 is returned for this mass.
        pooled = []
        for peak in sorted(masses):
            unresolved = [a for m, a in isotopic_cluster.items() if abs(
                m - peak) <= self.correction_limit]
            pooled.append(sum(unresolved))
        return pooled

    def get_mass_distribution_vector(self):
        """Get mass distribution vector (at natural abundancy) for non-tracers elements.

        Based on the elemental compositions of both metabolite's and derivative's moieties.

        Important:
            This methods needs to compute the full isotopic cluster,
            which is an expensive operation.

        Returns:
            list: mass distribution vector
        """
        iso_clust = self.get_isotopic_cluster()
        if iso_clust is None:  # all atoms are either tracer or ignored
            return [1.]     # same behavior as LowRes.
        minimum_mass = D(0)
        for element, n_elements in self.correction_formula.items():
            minimum_mass += n_elements * self.data_isotopes[element]["mass"][0]
        id_map = self.get_tracershifted_peaks_between(
            minimum_mass, max(iso_clust.keys()))
        mid = self.get_peaks_around(iso_clust, id_map)
        logger.debug("Done computing mass distribution vector for non-tracers "
                     "elements of %s (high-resolution method): %s", self.label, mid)
        return [float(x) for x in mid]

    def _correctionmatrix_combination(self):
        """Return the correction matrix constructed from the high-resolution correction vector (isotopic cluster).

        About the correction of tracer purity and natural abundance
        * Only atoms in *formula* are concerned; atoms of tracer's element in the derivative
          are already corrected in the correction_vector.
        * By default, we assume a perfect purity (see __init__).

        Returns:
            array: correction_matrix
        """
        n_tracers = self.formula[self._tracer_el]
        data_tracer = self.data_isotopes[self._tracer_el]
        n_tracer_isotopes = len(data_tracer["mass"])
        # Mass distribution vector without tracer
        isoclust_notracer = self.get_isotopic_cluster()
        if isoclust_notracer is not None:
            correction_vector = np.array(
                [(i, j) for i, j in isoclust_notracer.items()])
        main_peaks = self.get_tracershifted_peaks_between(self.molecular_weight,
                                                          self.molecular_weight + self.mzshift_tracer * n_tracers + D(0.5))
        # Prepare the Correction matrix
        n_isotopologues = n_tracers + 1
        correction_matrix = np.zeros((n_isotopologues, n_isotopologues))
        # For each measured peak, we compute the corresponding isotopic_cluster
        for n_traced_atoms in range(n_isotopologues):
            data = {}
            if isoclust_notracer is not None:
                data["cluster_notracer"] = correction_vector
            # Correct the tracer purity and natural abundance
            if n_traced_atoms:
                data["purity_tracer"] = self._get_block_n(data_tracer["mass"],
                                                          self.tracer_purity,
                                                          n_atoms=n_traced_atoms,
                                                          n_isotopes=n_tracer_isotopes)
            if n_tracers-n_traced_atoms:
                if self.correct_NA_tracer:
                    data["NA_tracer"] = self._get_block_n(data_tracer["mass"],
                                                          data_tracer["abundance"],
                                                          n_atoms=n_tracers-n_traced_atoms,
                                                          n_isotopes=n_tracer_isotopes)
                else:
                    data["NA_tracer"] = self._get_block_1(data_tracer["mass"][0],
                                                          n_tracers-n_traced_atoms)
            # Isotopic cluster with this combination of tracers
            iso_clust = self._combine_blocks(data)
            # Pool together unresolved peaks
            column = self.get_peaks_around(iso_clust, main_peaks)
            # Fill the corresponding column of the correction matrix
            correction_matrix[:, n_traced_atoms] = column
        logger.debug("Done computing correction matrix (isotopic-cluster method)"
                     " for %s: %s", self.label, correction_matrix.tolist())
        return correction_matrix

    def compute_correction_matrix(self):
        """Returns the correction matrix taking into account all parameters.

        Attention:
            Does not set :py:attr:`~correction_matrix` if called directly.

        Returns:
            array: the correction matrix
        """
        logger.debug("Computing correction matrix for %s...", self.label)
        n_tracer_isotopes = len(
            self.data_isotopes[self._tracer_el]["abundance"])
        assert n_tracer_isotopes > 1, "Unexpected number of isotopes for tracer ({}).".format(
            n_tracer_isotopes)
        if n_tracer_isotopes == 2:
            correction_matrix = self._correctionmatrix_convolution()
        else:
            correction_matrix = self._correctionmatrix_combination()
        return correction_matrix
