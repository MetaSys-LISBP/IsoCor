..  _FAQ:

Frequently asked questions
********************************************************************************

.. seealso:: If you wonder how to make the most out of IsoCor, have a look at the :ref:`Tutorials`.


Wait... I needed to correct something?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't fully understand why you should correct your MS isotopic data,
we invite you to have a look at `Midani et al. 2017 <https://doi.org/10.1016/j.ab.2016.12.011>`_ excellent review.

..
  If you would like to know more about IsoCor correction process, please take the time to scroll through the :ref:`Theory` section.
  It will drive you through several correction examples, from typical to edge cases.

Finally, practical examples are provided in the :ref:`Tutorials`.


What are the alternatives to IsoCor?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You will find scripts for correction of HRMS data out there, but we won’t recommend any since,
to the best of our knowledge, they implement algorithms that partly fail for high-resolution datasets (see IsoCor v2 publication).

+--------------+----------+----------------------+--------------------+------------------------------------------------------------------+---------------------------+
| Tool         | Has GUI? | MS resolution?       | Tracers?           | Reference                                                        | Comment                   |
+==============+==========+======================+====================+==================================================================+===========================+
| AccuCor      | No       | All                  | 2H,13C,15N         | `Su et al. 2017 <https://doi.org/10.1021/acs.analchem.7b00396>`_ | Faulty at High-resolution |
+--------------+----------+----------------------+--------------------+------------------------------------------------------------------+---------------------------+
| PyNAC        | No       | UltraHigh only       | 2H,13C,15N         | `Carreer et al. 2013 <https://doi.org/10.3390/metabo3040853>`_   | none                      |
+--------------+----------+----------------------+--------------------+------------------------------------------------------------------+---------------------------+
| IsoCorrectoR | No       | Low & UltraHigh only | All                | `GitHub project <https://github.com/chkohler/IsoCorrectoR>`__    | none                      |
+--------------+----------+----------------------+--------------------+------------------------------------------------------------------+---------------------------+
| ElemCor      | Yes      | All                  | 2H,13C,15N,18O,34S | `GitHub project <https://github.com/4dsoftware/elemcor>`__       | Faulty at High-resolution |
+--------------+----------+----------------------+--------------------+------------------------------------------------------------------+---------------------------+
| IsoCor       | Yes      | All                  | All                | `GitHub project <https://github.com/MetaSys-LISBP/IsoCor_v2>`__  | none                      |
+--------------+----------+----------------------+--------------------+------------------------------------------------------------------+---------------------------+

.. note:: If you would like your software to appear in this list, please get in touch with us.


How many peaks should I measure?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For a compound with :math:`n` atoms of the tracer element, you should measure :math:`n+1` peaks.


What mass fractions should I measure?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For a compound with :math:`n` atoms of the tracer element, you should measure
the :ref:`mass fractions <mass fractions>` corresponding to the compound having
incorporated 0, 1, ..., n isotopic tracers.


How to add a new metabolite/derivative into the database?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Open the relevant database file with a rustic text editor (e.g. Notepad++) and add a new
row in your file following the format described in :ref:`Input data`.

Database files are created by default at the first run of isocor in '/user/isocordb'. Additional metabolites and derivatives databases can also be defined, as described in :ref:`Input data`.

Take care not to modify the file format, nor its structure.
A typical error comes from Excel replacing '.' to ',' in floats.



What elemental formula should I declare into the database?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Obviously, errors in elemental formulas will result in erroneous
:ref:`isotopologue distributions <isotopologue distribution>`; thus special care must be taken
when defining these formulas. Details on the elemental formulas to be declared in IsoCor
can be found in :ref:`Tutorial section on formulas <formulas>`.


Should I tailor ‘natural abundance’ of isotopes for my experiment?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The abundance of each isotope in
natural samples depends on their origin. For instance, marine organisms have been
reported to have slightly less :sup:`13`\ C than land plants [IUPAC2016]_.
Ideally, you should measure the exact abundance of each isotope present
in an unlabeled sample prior to the labeling experiment. However, most of the time such an
experiment would require too much resources for a negligible gain in precision, as we previously
found [Millard2014]_. The default values should be good enough for most users, unless you work
with strongly exotic material.


Where does the default values for natural abundance and mass come from?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
From IUPAC [IUPAC2013]_.


Should I correct the tracer purity for my experiment?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Yes, if you know it. The purity of your tracer should be available from your
provider of labeled compound.

..seealso:: :ref:`Isotopic purity and natural abundance of the tracer`


What is the default value for the tracer purity?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default, we assume a perfect tracer purity.


Should I correct natural abundance of the tracer for my experiment?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Yes, you should correct for the presence of isotopes at natural abundance in unlabeled
positions of non-uniformally labeled nutrients.

..seealso:: :ref:`Isotopic purity and natural abundance of the tracer`


How does IsoCor performs its corrections?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Please have a look at the examples in the Tutorials section.
If you are looking for something more detailed, we invite you to review our source code [git depot](https://github.com/MetaSys-LISBP/IsoCor).
Also, have a look at the logs in Verbose logs mode; all the intermediate results (correction vector used to construct the correction matrix, correction matrix, etc)
will allow you to reproduce the results with pen and paper.

How is computed the mean enrichment?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The mean isotopic enrichment of a metabolite refers to the mean content in isotopic tracer in the
metabolite, expressed as the relative fraction of total atoms of its element in the metabolite. This
information is particularly useful for the quantification of split ratios between two metabolic pathways
resulting in different content of tracer.
IsoCor calculates the mean enrichment (:math:`ME`) using the following formula:

:math:`ME = \frac{^{n}_{i=0}M_{i}.i}{n}`


I would like a new feature.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We would be glad to improve IsoCor. Please get in touch with us so we could discuss your problem. [issue tracker].


.. [IUPAC2013] Isotopic Compositions of the Elements 2013, Pure Appl. Chem., 2016, Vol. 88, No. 3, pp. 293-306, https://doi.org/10.1515/pac-2015-0503
.. [IUPAC2016] Isotope-abundance variations and atomic weights of selected elements: 2016 (IUPAC Technical Report) https://doi.org/10.1515/pac-2016-0302
.. [Millard2014] Isotopic studies of metabolic systems by mass spectrometry: using Pascal's triangle to produce biological standards with fully controlled labeling patterns, 2014, Anal. Chem., 86(20):10288-10295, https://doi.org/10.1021/ac502490g
