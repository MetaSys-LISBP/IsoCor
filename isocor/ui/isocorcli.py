import argparse
import isocor as hr
import isocor.ui.isocordb
import pandas as pd
import io
import logging
from pathlib import Path
import sys


def process(args):
    # create logger (should be root to catch all 'mscorrectors' loggers)
    logger = logging.getLogger()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    # sends logging output to sys.stderr
    strm_hdlr = logging.StreamHandler()
    strm_hdlr.setFormatter(formatter)
    logger.addHandler(strm_hdlr)

    if hasattr(args, 'verbose'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # create environment
    baseenv = isocor.ui.isocordb.EnvComputing()
    if hasattr(args, 'I'):
        baseenv.registerIsopotes(Path(args.I))
    else:
        baseenv.registerIsopotes()
    if hasattr(args, 'D'):
        baseenv.registerDerivativesDB(Path(args.D))
    else:
        baseenv.registerDerivativesDB()
    if hasattr(args, 'M'):
        baseenv.registerMetabolitesDB(Path(args.M))
    else:
        baseenv.registerMetabolitesDB()

    try:
        # get correction parameters
        data_isotopes = baseenv.dictIsotopes
        tracer = args.tracer
        if not(tracer in baseenv.dfIsotopes['name'].unique()):
            raise ValueError(
                "Can't find tracer named '{}'. Eventually check the case in your Isotopes file".format(tracer))
        tracer_purity = getattr(args, 'tracer_purity', None)
        if tracer_purity:
            if any(i < 0 for i in tracer_purity) or any(i > 1 for i in tracer_purity) or sum(tracer_purity) != 1:
                raise ValueError(
                    "Purity values ({}) should be within the range [0, 1], and their sum should be 1.".format(tracer_purity))
        correct_NA_tracer = True if hasattr(
            args, 'correct_NA_tracer') else False
        resolution = getattr(args, 'resolution', None)
        mz_of_resolution = getattr(args, 'mz_of_resolution', None)
        resolution_formula_code = getattr(
            args, 'resolution_formula_code', None)
        if resolution_formula_code == 'datafile':
            useformula = False
        else:
            useformula = True
        HRmode = resolution or mz_of_resolution or resolution_formula_code
        if HRmode:
            if not resolution:
                raise ValueError(
                    "Applying correction to high-resolution data: 'resolution' should be provided.")
            if not mz_of_resolution:
                raise ValueError(
                    "Applying correction to high-resolution data: 'mz_of_resolution' should be provided.")
            if not resolution_formula_code:
                raise ValueError(
                    "Applying correction to high-resolution data: 'resolution_formula' should be provided.")
            if resolution <= 0:
                raise ValueError(
                    "Resolution '{}' should be a positive number.".format(resolution))
            if mz_of_resolution <= 0:
                raise ValueError(
                    "mz at which resolution is measured '{}' should be a positive number.".format(mz_of_resolution))

        baseenv.registerDatafile(Path(args.inputdata), useformula)
    except Exception as err:
        logger.error(
            "wrong parameters. Check for errors above. {}".format(err))
        raise

    # log general information on the process
    logger.info('------------------------------------------------')
    logger.info("Correction process")
    logger.info('------------------------------------------------')
    logger.info("   data files")
    logger.info("      data file: {}".format(args.inputdata))
    logger.info("      derivatives database: {}".format(
        getattr(args, 'D', 'Derivatives.dat')))
    logger.info("      metabolites database: {}".format(
        getattr(args, 'M', 'Metabolites.dat')))
    logger.info("      isotopes database: {}".format(
        getattr(args, 'I', 'Isotopes.dat')))
    logger.info("   correction parameters")
    logger.info("      isotopic tracer: {}".format(tracer))
    logger.info("      correct natural abundance of the tracer element: {}".format(
        correct_NA_tracer))
    logger.info("      isotopic purity of the tracer: {}".format(tracer_purity))
    if HRmode:
        logger.info("      mode: high-resolution")
        logger.info("         formula code: {}".format(
            resolution_formula_code))
        if useformula:
            logger.info(
                "         instrument resolution: {}".format(resolution))
        if resolution_formula_code != 'constant':
            logger.info("         at mz: {}".format(mz_of_resolution))
    else:
        logger.info("      mode: low-resolution")
    logger.info("   natural abundance of isotopes")
    logger.info("   {}".format(data_isotopes))
    logger.info("   IsoCor version: {}".format(hr.__version__))

    # initialize error dict
    errors = {'labels': [], 'measurements': []}

    labels = baseenv.getLabelsList(useformula)
    logger.info('------------------------------------------------')
    logger.info('Constructing correctors for all (metabolite, derivative)...')
    logger.info('------------------------------------------------')
    dictMetabolites = {}
    for label in labels:
        try:
            logger.debug("constructing {}...".format(label))
            if HRmode:
                if not useformula:
                    resolution = label[2]
                    resolution_formula_code = 'constant'
                dictMetabolites[label] = hr.MetaboliteCorrectorFactory(
                    formula=baseenv.getMetaboliteFormula(label[0]), tracer=tracer, resolution=resolution, label=label[0],
                    data_isotopes=data_isotopes, mz_of_resolution=mz_of_resolution,
                    derivative_formula=baseenv.getDerivativeFormula(label[1]), tracer_purity=tracer_purity,
                    correct_NA_tracer=correct_NA_tracer, resolution_formula_code=resolution_formula_code,
                    charge=baseenv.getMetaboliteCharge(label[0]))
            else:
                dictMetabolites[label] = hr.MetaboliteCorrectorFactory(
                    formula=baseenv.getMetaboliteFormula(label[0]), tracer=tracer, label=label[0],
                    data_isotopes=data_isotopes,
                    derivative_formula=baseenv.getDerivativeFormula(label[1]), tracer_purity=tracer_purity,
                    correct_NA_tracer=correct_NA_tracer)
            logger.info("{} successfully constructed.".format(label))
        except Exception as err:
            dictMetabolites[label] = None
            errors['labels'] = errors['labels'] + [label]
            logger.error("cannot construct {}: {}".format(label, err))
            sys.exit(2)

    logger.info('------------------------------------------------')
    logger.info('Correcting raw MS data...')
    logger.info('------------------------------------------------')
    df = pd.DataFrame()
    for label in labels:
        metabo = dictMetabolites[label]
        series, series_err = baseenv.getDataSerie(label, useformula)
        for s_err in series_err:
            errors['measurements'] = errors['measurements'] + \
                ["{} - {}".format(s_err, label)]
            logger.error(
                "{} - {}: Measurement vector is incomplete, some isotopologues are not provided.".format(s_err, label))
        for serie in series:
            if metabo:
                try:
                    isotopic_inchi = metabo.isotopic_inchi
                    valuesCorrected = metabo.correct(serie[1])
                    logger.info("{} - {}: processed".format(serie[0], label))
                except Exception as err:
                    isotopic_inchi = ['']*len(serie[1])
                    valuesCorrected = ([pd.np.nan]*len(serie[1]), [pd.np.nan]
                                       * len(serie[1]), [pd.np.nan]*len(serie[1]), pd.np.nan)
                    logger.error("{} - {}: {}".format(serie[0], label, err))
                    errors['measurements'] = errors['measurements'] + \
                        ["{} - {}".format(serie[0], label)]
            else:
                isotopic_inchi = ['']*len(serie[1])
                valuesCorrected = ([pd.np.nan]*len(serie[1]), [pd.np.nan]
                                   * len(serie[1]), [pd.np.nan]*len(serie[1]), pd.np.nan)
                errors['measurements'] = errors['measurements'] + \
                    ["{} - {}".format(serie[0], label)]
                logger.error(
                    "{} - {}: (metabolite, derivative) corrector could not be constructed.".format(serie[0], label))
            for i, line in enumerate(zip(*(serie[1], valuesCorrected[0], valuesCorrected[1], valuesCorrected[2], [valuesCorrected[3]]*len(valuesCorrected[0])))):
                df = pd.concat((df, pd.DataFrame([line], index=pd.MultiIndex.from_tuples([[serie[0], label[0], label[1], i, isotopic_inchi[i]]], names=[
                    'sample', 'metabolite', 'derivative', 'isotopologue', 'isotopic_inchi']), columns=['area', 'corrected_area', 'isotopologue_fraction', 'residuum', 'mean_enrichment'])))

    # summary results for logs
    logger.info('------------------------------------------------')
    logger.info("Correction process summary")
    logger.info('------------------------------------------------')
    logger.info("   number of samples: {}".format(
        len(baseenv.getSamplesList())))
    if useformula:
        logger.info(
            "   number of (metabolite, derivative): {}".format(len(labels)))
    else:
        logger.info(
            "   number of (metabolite, derivative, resolution): {}".format(len(labels)))
    nb_errors = len(errors['labels']) + len(errors['measurements'])
    logger.info("   errors: {}".format(nb_errors))
    if nb_errors:
        logger.info("      {} errors during construction of (metabolite, derivative) correctors".format(
            len(errors['labels'])))
        logger.info("      {} errors during correction of measurements".format(
            len(errors['measurements'])))
        logger.info("      detailed information on errors are provided above.")

    output = io.StringIO()
    df.to_csv(output, sep='\t')
    output.seek(0)
    print(output.read())


def parseArgs():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,
                                     description='correction of MS data for naturally occurring isotopes')

    parser.add_argument("inputdata", help="measurements file to process")
    parser.add_argument("-M", type=str, help="path to metabolites database")
    parser.add_argument("-D", type=str, help="path to derivatives database")
    parser.add_argument("-I", type=str, help="path to isotopes database")

    parser.add_argument("-t", "--tracer", type=str, required=True,
                        help='the isotopic tracer (e.g. "13C")')
    parser.add_argument("-r", "--resolution", type=float,
                        help='HR only: resolution of the mass spectrometer (e.g. "1e4")')
    parser.add_argument("-m", "--mz_of_resolution", type=float,
                        help='HR only: mz at which resolution is given (e.g. "400")')
    parser.add_argument("-f", "--resolution_formula_code", type=str,
                        choices=hr.HighResMetaboliteCorrector.RES_FORMULAS, help="HR only: spectrometer formula code")
    parser.add_argument("-p", "--tracer_purity", type=lambda s: [float(item) for item in s.split(',')],
                        help="purity vector of the tracer")
    parser.add_argument("-n", "--correct_NA_tracer",
                        help="flag to correct tracer natural abundance", action='store_true')
    parser.add_argument("-v", "--verbose",
                        help="flag to enable verbose logs", action='store_true')
    return parser


def start_cli():
    parser = parseArgs()
    args = parser.parse_args()
    process(args)
