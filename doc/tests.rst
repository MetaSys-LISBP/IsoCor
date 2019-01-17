..  _Unit tests:

Unit tests
================================================================================

Isotope correction is a complex task and we use (some) unit tests to make sure
that critical features are not compromised during development.

A total of 318 tests has been designed to test IsoCor from individual steps
(e.g. calculation of theoretical :ref:`mass fractions <mass fractions>` or correction matrices) to the
entire correction process.
Importantly, most of the tests compare intermediate (e.g. correction matrix) or
final (e.g. :ref:`isotopologue distribution <isotopologue distribution>`) calculations of IsoCor to theoretical results,
with algebraic equations provided in the code for manual check.

All situations that may be encountered (e.g. in terms of tracer, metabolite or MS :ref:`resolution <resolution>`) should
be covered by these tests.

You can run all tests by calling :samp:`pytest` in the shell at project's root directory
(it must be installed beforehand):

.. code-block:: bash

    pytest


To add a new test-case, see `pytest documentation <https://docs.pytest.org/en/latest/reference.html>`_.

Tests are stored in :file:`tests/` folder.


Isotopic clusters
--------------------------------------------------------------------------------

.. automodule:: isocor.tests.test_isotopic_cluster_LowRes
   :members:

.. automodule:: isocor.tests.test_isotopic_cluster_HighRes
   :members:


Minimal mass difference to distinguish two isotopic species
--------------------------------------------------------------------------------

.. automodule:: isocor.tests.test_m_min_constant
   :members:

.. automodule:: isocor.tests.test_m_min_orbitrap
   :members:


Correction matrix
--------------------------------------------------------------------------------

.. automodule:: isocor.tests.test_correction_matrix_LowRes
   :members:

.. automodule:: isocor.tests.test_correction_matrix_HighRes_resolved
   :members:

.. automodule:: isocor.tests.test_correction_matrix_HighRes_unresolved
   :members:


Correction process examples
--------------------------------------------------------------------------------

.. automodule:: isocor.tests.test_correction_process_LowRes
   :members:

.. automodule:: isocor.tests.test_correction_process_HighRes
   :members:

.. automodule:: isocor.tests.test_all_cases
  :members:


Misc.
--------------------------------------------------------------------------------

.. automodule:: isocor.tests.test_factory
  :members:

.. automodule:: isocor.tests.conftest
   :members:
