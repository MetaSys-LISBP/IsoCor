# IsoCor - **Iso**tope **Cor**rection for mass spectrometry labeling experiments

[![PyPI version](https://badge.fury.io/py/IsoCor.svg)](https://badge.fury.io/py/IsoCor)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/isocor.svg)](https://pypi.python.org/pypi/isocor/)
[![Build Status](https://travis-ci.com/MetaSys-LISBP/IsoCor.svg?branch=master)](https://travis-ci.com/MetaSys-LISBP/IsoCor)
[![Documentation Status](https://readthedocs.org/projects/isocor/badge/?version=latest)](http://isocor.readthedocs.io/?badge=latest)

[![IsoCor graphical user interface](https://raw.githubusercontent.com/MetaSys-LISBP/IsoCor/master/doc/_static/isocor_GUI.png)](https://isocor.readthedocs.io/en/latest/)


## What is IsoCor?
**IsoCor is a scientific software dedicated to the correction of mass spectrometry (MS) data for naturally
occuring isotopes**.
IsoCor corrects raw MS data (mass fractions) for
naturally-occurring isotopes of all elements and purity of the
isotopic tracer.
The output of IsoCor is the isotopologue distribution of the molecule
(i.e. the relative fractions of molecular entities differing only in the number
of isotopic substitutions of the tracer). IsoCor also calculates
the mean enrichment (i.e. the mean isotopic content in the molecule) in metabolites.

It is one of the routine tools that we use at the [MetaSys team](http://www.lisbp.fr/en/research/molecular-physiology-and-metabolism/metasys.html) and [MetaToul platform](http://www.metatoul.fr) in isotopic studies of metabolic systems.

The code is open-source, and available under a GPLv3 license. Additional information can be found in [IsoCor publication](https://doi.org/10.1093/bioinformatics/btz209).

Detailed documentation can be found online at Read the Docs ([https://isocor.readthedocs.io/](https://isocor.readthedocs.io/)).
Check out the [Tutorials](https://isocor.readthedocs.io/en/latest/tutorials.html) to use the best correction option!

## Key features
* **correction of naturally occuring isotopes**, both for non-tracer and tracer elements,
* **correction of tracer purity**,
* shipped as a library with both a **graphical and command line interface**,
* mass-spectrometer and resolution agnostic,
* can be applied to singly- and multiply-charged ions
* can be used with any tracer element (having two or more isotopes)
* account for the contribution of derivatization steps (if any),
* generate isotopic InChIs of the tracer isotopologues,
* open-source, free and easy to install everywhere where Python 3 and pip run,
* biologist-friendly.

## Quick-start
IsoCor requires Python 3.5 or higher and run on all plate-forms.
Please check [the documentation](https://isocor.readthedocs.io/en/latest/quickstart.html) for complete
installation and usage instructions.

Use `pip` to **install IsoCor from PyPi**:

```bash
$ pip install isocor
```

Then, start the graphical interface with:

```bash
$ isocor
```

IsoCor is also available directly from command-line and as a Python library.

## Bug and feature requests
If you have an idea on how we could improve IsoCor please submit a new *issue*
to [our GitHub issue tracker](https://github.com/MetaSys-LISBP/IsoCor/issues).


## Developers guide
### Contributions
Contributions are very welcome! :heart:

Please work on your own fork,
follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide,
and make sure you pass all the tests before a pull request.

### Local install with pip
In development mode, do a `pip install -e /path/to/IsoCor` to install
locally the development version.

### Unit tests
Isotope correction is a complex task and we use unit tests to make sure
that critical features are not compromised during development.

You can run all tests by calling `pytest` in the shell at project's root directory.

### Build the documentation locally
Build the HTML documentation with:

```bash
$ cd doc
$ make html
```

The PDF documentation can be built locally by replacing `html` by `latexpdf`
in the command above. You will need a recent latex installation.

## How to cite
Millard P., Delépine B., Guionnet M., Heuillet M., Bellvert F. and Letisse F. IsoCor: isotope correction for high-resolution MS labeling experiments. Bioinformatics, 2019, [doi: 10.1093/bioinformatics/btz209](https://doi.org/10.1093/bioinformatics/btz209)

## Authors
Baudoin Delépine, Matthieu Guionnet, Pierre Millard

## Contact
:email: Pierre Millard, millard@insa-toulouse.fr
