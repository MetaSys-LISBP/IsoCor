"""IsoCor package initialisation.

We expose the Factory and the *metabolite corrector* classes at the package level
for conveniance.
"""

__version__ = '2.1.2'

from isocor.mscorrectors import MetaboliteCorrectorFactory
from isocor.mscorrectors import LowResMetaboliteCorrector, HighResMetaboliteCorrector
