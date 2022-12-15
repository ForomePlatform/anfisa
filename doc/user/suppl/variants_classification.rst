.. _variants_classification_algorithm:

Variants Classification algorithm
=================================
The clinical classification of the sequence variants is calculated by a combination of intermediate parameters.
The parameters are comprised of information programmatically assessed from various public databases,
which include variant consequences, clinical significance allocated for the variant
by HGMD and ClinVar databases and use of the genetic in-silico prediction tools, such as PolyPhen2, SIFT, FATHMM,
Mutation Assessor and Mutation Taster.

The variant’s consequence is divided into two groups identified either as a putative loss-of-function variant
or as unknown functional impact. By default, this grouping is the first step in a variant’s classification in Anfisa.
The second step is the filtering against the tags assigned to the variant in HGMD and ClinVar databases.
The four values (consensus benign, consensus pathogenic, uncertain predictions and absent predictions)
could be assigned to the variants.

The "*consensus benign*" or "*pathogenic*" values are assigned to the variants for which HGMD and ClinVar tags
are either concordant in both databases or have been tagged as consensus benign or pathogenic
at least in one of the databases.
An uncertain prediction value is assigned for the variants with discordant HGMD and ClinVar tags.
For the variants with no consensus benign or pathogenic values, or variants that are absent from both databases,
in-silico prediction tools are applied as a third step in the variant’s classification.


