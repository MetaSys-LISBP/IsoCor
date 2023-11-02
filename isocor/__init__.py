"""IsoCor package initialisation.

We expose the Factory and the *metabolite corrector* classes at the package level
for conveniance.
"""

# Version number MUST be maintained here (x.y.z format)
__version__ = '2.2.2'

from isocor.mscorrectors import MetaboliteCorrectorFactory
from isocor.mscorrectors import LowResMetaboliteCorrector, HighResMetaboliteCorrector
