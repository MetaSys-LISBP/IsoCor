..  _Tutorials:

################################################################################
Tutorials
################################################################################

.. seealso:: If you have a question that is not covered in the tutorials, have a look
             at the :ref:`faq`.


.. _First time using IsoCor:

********************************************************************************
First time using IsoCor
********************************************************************************

..  _`Input data`:

Input data
================================================================================

IsoCor takes as input the raw MS data, i.e. :ref:`mass fractions <mass fractions>`
of the :ref:`isotopic cluster <isotopic cluster>`,
to calculate the corresponding :ref:`isotopologue distribution <isotopologue distribution>`,
hence providing quantitative information on the incorporation of labeling into metabolites.

The raw MS data and the information required to perform the correction (i.e. the natural abundance and exact mass of isotopes,
and a list of metabolites and derivatives moieties with their elemental formulas) are provided in flat text files.

At first start, IsoCor creates in the user directory a IsoCor data folder `isocordb` containing default database files.
These files can be edited and implemented according to the user's needs, as detailed below. Different database files can also be created
(e.g. to have specific project-related databases), as detailed below.

..  _`Measurements file`:

Measurements file
--------------------------------------------------------------------------------

**This file contains the raw MS data for each metabolite of each sample**,
i.e. the :ref:`mass fractions <mass fractions>` of the measured :ref:`isotopic cluster <isotopic cluster>`
that contain information on the :ref:`tracer isotopologues <tracer isotopologues>`.
For each metabolite you should always measure :math:`n+1` mass fractions,
where :math:`n` is the number of atoms of the tracer element in the metabolite.

The measurement file is a TSV file with one row by :ref:`isotopologue <isotopologues>` and the following columns:

:sample: The sample name (optional); e.g. "Cloverfield 10".
:metabolite: The metabolite name that represents the metabolite moiety, as it is referred in the metabolite database (*metabolites.dat*); e.g. "PEP".
:derivative: The derivative name (optional) that represents the derivative moiety, as it is referred in the derivative database (*derivatives.dat*); e.g. "TMS".
:isotopologue: The index of the peak measured, as an integer; e.g. '0' for the M0 peak that does not have any mass shift.
:area: The measured :ref:`mass fractions <mass fractions>`; e.g. "4242.42".
:resolution (optional): The MS resolution of the corresponding :ref:`mass fractions <mass fractions>`; e.g. "60000". Note the *all* mass fractions of a given isotopic cluster must have the same resolution.

:download:`Example file <../isocor/data/Data_example.tsv>`.

.. note:: An example file is provided with IsoCor. It is created at the
          first run of IsoCor in your user directory (`<youruserdirectory>/isocordb/Data_example.tsv`).

.. topic:: About derivatives

          The derivative field is optional and should be declared only if:

          1. a derivatization step was performed before MS analysis,
          2. some atoms of the derivative remains in the molecular entity that gives rise to
             measured :ref:`isotopic cluster <isotopic cluster>`.

.. seealso::
  :ref:`Declaration of elemental formulas: "metabolite" and "derivative" moieties <Formulas>`


Database files
--------------------------------------------------------------------------------

The exact mass and natural abundance of each isotope and the elemental formulas
used for correction have to be defined carefully, otherwise the correction will be wrong.

IsoCor rely on several flat-files to store this information.
Pre-configured files are shipped with IsoCor and created at the first run of IsoCor.
Those database should be modified according to the user needs.
They are **located in IsoCor data directory**, in user main directory: `<youruserdirectory>/isocordb/`.

.. note:: IsoCor is case sensitive; i.e. two metabolites
          or derivatives with the same name but different cases will
          be considered as two distinct entities.


*Isotopes database (Isotopes.dat)*
--------------------------------------------------------------------------------

This file stores **the exact mass and natural abundance of all stable isotopes of each element**, given as relative fractions.

It is a TSV file with one row by isotope and the following columns:

:element: The element symbol of the isotope; e.g. "C".
:mass: The exact mass of this isotope; e.g. "13.003354835" for :sup:`13`\ C.
:abundance: The relative abundance of this isotope normalized to 1; e.g. "0.0107" for :sup:`13`\ C.

:download:`Example file <../isocor/data/Isotopes.dat>`.

A pre-configured isotopes database can be found in IsoCor data directory and should be edited according to the users needs.
It is located in user main directory at `<youruserdirectory>/isocordb/Isotopes.dat`.

.. warning:: The isotopes database is always loaded from IsoCor data directory,
             i.e. from `<youruserdirectory>/isocordb/Isotopes.dat`.

.. note:: **All** elements should be declared, including elements with only one isotope (with its abundance set to 1).
          This is required for accurate correction of high-resolution data.

.. note:: For elements with gaps in the list of nominal mass of isotopes (e.g. for sulfur with isotopes :sup:`33`\ S, :sup:`34`\ S, :sup:`36`\ S, but not :sup:`35`\ S),
          declare the missing isotope(s), with the exact mass set at the missing integer(s), and an abundance of 0 (as done in the example file for sulfur).


..  _`Metabolites database`:

*Metabolites database (Metabolites.dat)*
--------------------------------------------------------------------------------

This file stores **elemental formulas of the metabolites**.

It is a TSV file with the following columns:

:name: Metabolite name or abbreviation; e.g. "pyruvic acid" or "PYR".
:formula: Elemental formula of the metabolite moiety of the molecular entity that
          gives rise to the measured :ref:`isotopic cluster <isotopic cluster>`; e.g. "C\ :sub:`3`\ H\ :sub:`4`\ O\ :sub:`3`\ ". See also :ref:`Formulas`.
:charge: Charge state of the detected ion; e.g. "-1" for singly-charge ions or "-2" for doubly-charge ions.
:inchi: InChI (may refer to the metabolite, the detected ion, or any other chemical substance); e.g. "InChI=1S/C4H4O4/c5-3(6)1-2-4(7)8/h1-2H,(H,5,6)(H,7,8)/p-2/b2-1+" for fumarate. This field is optional.

:download:`Example file <../isocor/data/Metabolites.dat>`.

A pre-configured metabolites database can be found in IsoCor data directory and should be edited according to the users needs.
It is located in user main directory at `<youruserdirectory>/isocordb/Metabolites.dat`.


*Derivatives database (Derivatives.dat)*
--------------------------------------------------------------------------------

This file stores **elemental formulas of chemical derivatives** that have to be
considered for the isotopic correction of metabolites derivatized prior to
MS analysis.

It is a TSV file with the following columns:

:name: Derivative name or abbrevation; e.g. "t-butyldimethyl-silylation" or "M-57".
:formula: Elemental formula of the derivative moiety of the molecular entity that
          gives rise to the measured :ref:`isotopic cluster <isotopic cluster>`; e.g. "Si\ :sub:`2`\ C\ :sub:`8`\ H\ :sub:`21`\ ". See also :ref:`Formulas`.

:download:`Example file <../isocor/data/Derivatives.dat>`.

A pre-configured derivatives database can be found in IsoCor data directory and should be edited according to the users needs.
It is located in the user main directory at `<youruserdirectory>/isocordb/Derivatives.dat`.


*Custom databases*
--------------------------------------------------------------------------------

IsoCor data directory is created at the first run of IsoCor with pre-configured
databases files in the user main directory (`<youruserdirectory>/isocordb/`).
These files should be edited according to the users needs,
e.g. to add some metabolites and derivatives formulas.

Alternatively, users can select at runtime a custom folder from which metabolites
and derivatives will be loaded ('Metabolites.dat' and 'Derivatives.dat') with
the 'Databases Path' button.
It is especially useful to define project-based database files.

.. warning::
   Importantly, 'Isotopes.dat' is always loaded from IsoCor data directory ('<youruserdirectory>/isocordb/Isotopes.dat') and will not be loaded from a custom databases folder.

..  _CorrectionOptions:

Correction parameters
================================================================================

IsoCor provides several options to adapt to many situations that can be encountered
in terms of isotopic tracer, sample processing,
:ref:`resolution <resolution>` of the MS analyzer, etc.

:Measurements file: Path to the :ref:`Measurements file`.
:Isotopic tracer: The tracer used for your experiment. Available tracers are imported from *isotopes.dat* database file.
:Resolution: :ref:`Resolution` of the MS analyzer.
:Resolution measured at: m/z at which the :ref:`resolution <resolution>` is given.
:Resolution formula: The relationship between the operating :ref:`resolution <resolution>` and the resolution at m/z of the measured metabolite moiety depends on the MS analyzer, which has to be selected. If 'datafile' is selected, resolution should be provided for all mass fractions in the measurements file.
:Tracer purity: Correct for the presence of unlabeled atoms at labeled positions, using the relative abundance of each isotope of the tracer element at labeled positions. Default is to assume a perfect purity (i.e. tracer isotope=1).
:Correct natural abundance of the tracer element: Correct for natural abundance of the tracer element at unlabeled positions. Default is no correction.
:Output data path: Path to the :ref:`Output data`. A log file with the same name will be created in the same directory, with a '.log' extension.
:Verbose logs: If set, the log-file will contain all information necessary to check intermediate results of the correction process.

.. seealso:: Tutorial: :ref:`Isotopic purity and natural abundance of the tracer`.



..  _`Output data`:

Output files
================================================================================

Result file
--------------------------------------------------------------------------------

The result file is a TSV file with the following columns:

:sample: Name of the sample, as it was provided in the :ref:`Measurements file`.
:metabolite: Name of the metabolite, as it was provided in the :ref:`Measurements file`.
:derivative: Name of the derivative, as it was provided in the :ref:`Measurements file`.
:isotopologue: The index of the peak measured, as an integer; e.g. '0' for the M\ :sub:`0`\  peak that does not have any mass shift, as it was provided in the :ref:`Measurements file`.
:isotopic_inchi: Isotopic InChI of the corresponding tracer isotopologue (or just the isotopic layer if no InChI has been provided in the :ref:`Metabolites database` file), as detailed :ref:`here <isotopic_inchi>`; e.g. with isotopic layer '/a(C1+1),(C3+0)' for the M\ :sub:`1`\  :sup:`13`\ C-isotopologue of fumarate.
:area: The measured peak intensity; e.g. '42.5', as it was provided in the :ref:`Measurements file`.
:corrected_area: The corrected area.
:isotopologue_fraction: The abundance of each :ref:`isotopologue <Isotopologues>` (corrected area normalized to 1).
:residuum: Residuum of the fit (difference between experimental and optimal isotopologue distribution, normalized to 1).
:mean_enrichment: Mean molecular content in isotopic tracer in the metabolite.


Log file
--------------------------------------------------------------------------------

A log file is created in the same directory as the Result file to store correction parameters (for reproducibility),
with a '.log' extension.

Extensive information on the correction process (correction vector, correction matrix, intermediary results, etc.)
can be found in the log file if 'Verbose logs' option has been checked.


Warning and error messages
--------------------------------------------------------------------------------

Error messages are explicit. You should examine carefully any warning/error message.
After correcting the problem, you might have to restart IsoCor (to reload databases files)
and perform the correction again.


..  _Formulas:

********************************************************************************
Declaration of elemental formulas: metabolite and derivative moieties
********************************************************************************

This section provides guidelines for the definition of elemental formulas of "metabolite" and "derivative" moieties.
It also provides representative examples to cover a large panel of MS and MS/MS methods
dedicated to quantitative isotopic analysis.

What is in the elemental formula
================================================================================

**Elemental formulas must be defined according to the molecular entity that gives
rise to the measured** :ref:`isotopic cluster <isotopic cluster>`.
It may correspond (but not necessarily) to the elemental formula of the detected ion.

For instance, in the following situations, the formulas should include:

- for MS measurements: all atoms of the detected ion
- for MS/MS measurements, with all tracer atoms in the detected ion: only atoms of the detected ion
- for MS/MS measurements, with no tracer atoms in the detected ion: only atoms of the complement (neutral fragment)


Metabolite vs. derivative formulas
================================================================================

**All atoms of the molecular entity that gives rise to the measured** :ref:`isotopic cluster <isotopic cluster>`
**should be declared strictly once in a formula, either as a "metabolite" or a "derivative" moiety.**

Atoms that originate from the metabolite should be declared in the file "*metabolites.dat*",
and atoms that originate from the derivative (if any) should be declared in the file "*derivatives.dat*".

A derivative moiety should thus be declared only if a derivatization step was performed
before MS analysis. Importantly, we consider that *the derivative moiety do not contain any tracer atom*.
Therefore, all its atoms (including atoms of the tracer element) are expected to
be at natural isotope abundance and will be corrected as such.
This is obviously not the case for the metabolite moiety that do incorporate tracer
atoms and is thus corrected differently.
It follows that, to ensure the accurate correction of the measured :ref:`isotopic cluster <isotopic cluster>`,
the atoms originated from the derivative moiety must be declared separately
from those originated from the metabolite moiety (respectively into *derivatives.dat* and *metabolites.dat*).


.. topic:: Example 1 - MS analysis: Pyruvate

          Pyruvic acid (C\ :sub:`3`\ H\ :sub:`4`\ O\ :sub:`3`\ ) can be analyzed by LC-MS using multiple
          ion monitoring (MIM) in the negative mode, and the measured :ref:`isotopic cluster <isotopic cluster>` originates from the molecular ion [C\ :sub:`3`\ H\ :sub:`3`\ O\ :sub:`3`\ ]\ :sup:`-`\ , then the
          formula to use for correction is C\ :sub:`3`\ H\ :sub:`3`\ O\ :sub:`3`\ .
          This formula must be set into *metabolites.dat* and referred to
          by its associated name into the measurements file.

.. topic:: Example 2 - MS/MS analysis, with no tracer atoms in the detected ion: PEP

          Phosphoenolpyruvate (PEP) can be analyzed using the MS/MS method developed by
          Kiefer et al. (2007). The fragmentation of phosphorylated metabolites
          results in the efficient release of [PO\ :sub:`3`\ ]\ :sup:`-`\  or [H\ :sub:`2`\ PO\ :sub:`4`\ ]\ :sup:`-`\  ions,
          allowing highly sensitive measurement of :ref:`isotopologue distributions <isotopologue distribution>`
          in these compounds in the multiple reaction monitoring
          (MRM) mode. This is achieved by selecting MRM
          transitions in which phosphate ions are detected but which
          encode the :ref:`isotopic cluster <isotopic cluster>` of the complement, i.e., the
          part of the molecule that remains after loss of the phosphate
          ion that is actually detected.
          In the case of PEP (C\ :sub:`3`\ H\ :sub:`5`\ O\ :sub:`6`\ P), for which the molecular ion that is analyzed is [C\ :sub:`3`\ H\ :sub:`4`\ O\ :sub:`6`\ P]\ :sup:`-`\ , the
          analysis is based on MRM transitions in which [PO\ :sub:`3`\ ]\ :sup:`-`\  ions are
          used, meaning that the :ref:`isotopic cluster <isotopic cluster>` is actually measured for
          the complement fragment C\ :sub:`3`\ H\ :sub:`4`\ O\ :sub:`3`\ . Hence, the formula to
          enter in *metabolites.dat* is C\ :sub:`3`\ H\ :sub:`4`\ O\ :sub:`3`\ .

.. topic:: Example 3 - MS analysis of derivatized metabolites with in source fragmentation, with all tracer atoms in the detected ion: TBDMS-derivatized Alanine

          Alanine (C\ :sub:`3`\ H\ :sub:`7`\ O\ :sub:`2`\ N) can be analyzed by GC-MS after t-butyldimethyl-silylation (TBDMS derivatization).
          A fragment that is classically used for :sup:`13`\ C-metabolic flux analysis is the 'M-57'
          fragment that contains all atoms the compound of interest and two TBDMS groups,
          one of which lose the fragment [C\ :sub:`4`\ H\ :sub:`9`\ ].
          The elemental formula of the two TBDMS groups excluding the latter fragment (i.e. [Si\ :sub:`2`\ C\ :sub:`8`\ H\ :sub:`21`\ ])
          must be declared into *derivatives.dat* since it will be present in the molecular entity that gives rise to the measured :ref:`isotopic cluster <isotopic cluster>`.
          Meanwhile, the elemental composition of the alanine moiety of the detected ion (i.e. [C\ :sub:`3`\ H\ :sub:`5`\ O\ :sub:`2`\ N]) must
          be declared as the "metabolite moiety", thus into *metabolites.dat*.

.. topic:: Example 4 - MS/MS analysis, with all tracer atoms in the detected ion

          In this situation where the fragment ion which is detected gives rise to the measured :ref:`isotopic cluster <isotopic cluster>`, the elemental
          formula to declare in IsoCor is the formula of the fragment ion. Atoms of the fragment that originate from the metabolite should be declared
          into *metabolites.dat*, and atoms that originate from the derivative should be declared into *derivatives.dat*.



..  _`Resolution of the MS analyzer`:

********************************************************************************
Resolution of the MS analyzer
********************************************************************************

This section provides guidelines to account for the :ref:`resolution <resolution>` of the MS analyzer.

Low-resolution
================================================================================

For low :ref:`resolution <resolution>` datasets collected at unitary resolution (i.e. typically R<1000), select "Low resolution".


High-resolution
================================================================================

For high :ref:`resolution <resolution>` datasets, accurate correction requires to know the resolution of the MS analyzer at the particular m/z of the
molecular entity that gives rise to the experimental :ref:`isotopic cluster <isotopic cluster>`.
It is used to identify the correct set of isotopic species that overlap with the masses
of the tracer isotopologues in the :ref:`isotopic cluster <isotopic cluster>`, and ultimately remove their contribution.

Typically, the :ref:`resolution <resolution>` of the MS analyzer is given at a specific m/z (defined during
instrument calibration). IsoCor estimates the resolution at the appropriate m/z,
provided this relationship is known. This relationship depends on each instrument and was implemented
for FT-ICR and Orbitrap analyzers.

We have also implemented an option to set a "constant resolution", i.e. which is considered to be
independent of the m/z.

Finally, the option "datafile" allows users to provide resolution of each mass fraction directly in the measurements file. Note that resolution must be the same for *all*
peaks of a given isotopic cluster.

.. note::
          If you want to use IsoCor with a high-resolution MS instrument
          that is not currently supported
          (and for which you have the mathematical relationship to calculate the :ref:`resolution <resolution>` at
          a given m/z from the resolution at the calibration mass), please contact us.



..  _`Isotopic purity and natural abundance of the tracer`:

********************************************************************************
Isotopic purity and natural abundance of the tracer
********************************************************************************

IsoCor provides options to correct (or not) for isotopic purity of the tracer and natural abundance of the tracer elements.
Ideally, you should correct the data for both isotopic purity of
the tracer and natural abundance of the tracer elements. By doing so, the output
data will readily reflect the incorporation of labeling
and will be comparable between metabolites.

However, this is not always possible (e.g. if the isotopic purity is not known it cannot be corrected),
nor desirable (e.g. if a tool downstream in your analysis pipeline will force you to perform some corrections).
In the end, the correction options must always be taken into account when interpreting
the data so you should choose them carefully.

.. warning:: The choice to correct isotopic purity and/or natural abundance of the tracer
            is absolutely critical for accurate interpretations of the output data (isotopologues distributions)!


Isotopic purity of the tracer
================================================================================

Labelled substrates are not isotopically pure, i.e. they are not 100 % enriched at
the 'labelled' position(s). The latter contain small fractions
of non-tracer isotopes for which MS data must be corrected.
To do so, the fractions of each isotope into the 'labelled' positions must be provided.
For example, if the content in :sup:`13`\ C atoms in each position
of a U-:sup:`13`\ C-labeled compound is 99 %, other 1 % being :sup:`12`\ C atoms, the purity must be entered as *12C=0.01* and *13C=0.99*.

.. note::
          If you do not want to correct :ref:`isotopic clusters <isotopic cluster>` for the isotopic
          purity of the substrate, or if you do not know it, just let the default value (purity = 1).

.. warning::
            Tracer purity correction is only valid if *all* the labelled
            positions of the substrate(s) have the same isotopic purity.
            It should be checked from the manufacturers or determined experimentally.

            When different labeled substrates are mixed, tracer purity correction also requires
            that all their labeled positions have the same isotopic purity.

.. topic:: Example: Unknown purity

          If the purity of the label input(s) is not known you will not be able to
          correct it, despite the fact that it could be significant.
          Therefore, you should take special care in the interpretation of mean enrichment which will be overestimated.

.. topic:: Example: Several inputs with distinct purity

          If two or more labeled inputs have highly different isotopic purity you will not be able to
          correct it properly.
          Therefore, you should take special care in the interpretation of mean enrichment.


Natural abundance of the tracer
================================================================================

When the label input is not uniformly labelled, it contains 'unlabelled'
positions in which the tracer isotope is usually
occurring at its natural abundance. The MS data can be
corrected for the contribution of these naturally occurring isotopes.

.. warning:: Correction for natural abundance of the tracer element is only valid when the isotopes of the tracer element occur at natural
           abundance into the unlabeled positions of the input substrate(s).
           It is typically the case but
           should be checked from the manufacturer or determined experimentally.


.. topic:: Example: Natural abundance and downstream analysis

         You must be aware of the corrections performed by downstream analysis tools
         and make sure that you do not correct something twice.

         In a :sup:`13`\ C-metabolic flux analysis experiment,
         *if the raw data has already been corrected for natural abundance of the tracer element*,
         the unlabeled position(s) of all carbon sources must be declared as unlabeled
         with a perfect purity when calculating fluxes (e.g. CO\ :sub:`2`\  input
         should be declared as: *12C=1.0*), which might be counter-intuitive since
         you knew they were at natural abundance.

         In contrast, *if the raw data was not corrected for natural abundance of the tracer element*,
         the unlabeled position(s) of all carbon sources must be declared at natural abundance when calculating fluxes (e.g. CO\ :sub:`2`\  input
         should be declared as: *12C=0.9893, 13C=0.0107*).
