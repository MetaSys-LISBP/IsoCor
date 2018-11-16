Definitions
------------------------------------------------

Some important definitions are provided in this section.

..  _isotopologues:

Isotopologues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Molecular entities that differ only in their isotopic composition (number
of isotopic substitutions), according to its IUPAC definition. It
consists of isotopic forms that either:

i. do not have the same isotopic
   composition but have the same nominal mass (e.g., :sup:`13`\ CH\ :sub:`3`\ NH\ :sub:`2`\ 
   and CH\ :sub:`2`\ DNH\ :sub:`2`\ )
ii. or have neither the same isotopic composition nor the same nominal mass (e.g., CH\ :sub:`4`\ , CH\ :sub:`3`\ D,
    CH\ :sub:`2`\ D\ :sub:`2`\ ). The ability of the MS analyzer to distinguish different isotopologues is determined only by the
    elemental formula of the molecule and the resolution of the MS analyzer.


..  _tracer isotopologues:

Tracer isotopologues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Isotopologues that differ only in their isotopic composition (number
of isotopic substitutions) of the tracer element (e.g. CH\ :sub:`3`\ NH\ :sub:`2`\ , CH\ :sub:`2`\ DNH\ :sub:`2`\  and CHD\ :sub:`2`\ NH\ :sub:`2`\  are considered as tracer
isotopologues in a :sup:`2`\ H-labeling experiments). A molecular entity containing :math:`n` tracer atoms has :math:`n+1` tracer isotopologues.
Tracer isotopologues have different nominal masses, hence they can be distinguished both at low and high MS resolution.


..  _isotopic cluster:

Isotopic cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Group of MS peaks that originate from a unique molecular entity, i.e. with the same elemental
composition but different isotopic compositions, according to its IUPAC definition. A given peak of the
isotopic cluster typically contains several isotopologues. The number and the nature of isotopologues overlapped
in each peak is determined only by the
elemental formula of the molecule and the resolution of the MS analyzer. The intensity of each peak depends on the
abundance of each isotopologue, and thus on the incorporation of tracer.


..  _mass fractions:

Mass fractions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The intensity or area of the peaks of the isotopic cluster that contain
information on the incorporation of tracer, i.e. of the MS peaks originating from the molecular entity
containing :math:`0, 1, ..., n` tracer atoms, where :math:`n` is the number of atoms of tracer element in this entity. Mass fractions
also contains the contribution of other isotopic species which must be removed. The set of overlapping isotopic species is determined only by the
elemental formula of the molecule and the resolution of the MS analyzer.


..  _isotopologue distribution:

Isotopologue distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Abundance of tracer isotopologues relative to the total pool of the tracer isotopologues.
It contains labeling information which is specific to the incorporation of tracer atoms.
Isotopologue distribution, obtained after correcting mass fractions for naturally occuring isotopes, is the output of IsoCor.


..  _resolution:

Resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Resolution measures of the ability of the MS analyzer to distinguish two peaks of slightly different mass-to-charge ratios :math:`\delta(M)` in a mass spectrum.
It is classically described as a fixed  value of :math:`M/\delta(M)`  (the
*nominal resolution*, defined as Full Width at Half
Maximum (FWHM) at a particular m/z). In order for the isotopic peaks to be well separated, the mass difference should be greater than
1.66 FWHM.
