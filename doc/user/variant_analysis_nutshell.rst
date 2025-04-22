.. _analysis_nutshell:

*******************************
Variant analysis in a nutshell
*******************************

The very brief instruction on installation and usage of AnFiSA.

#. Install AnFiSA via docker compose: https://github.com/ForomePlatform/deploy/blob/main/docker-compose/README.md
#. To analyze your data, use data processing pipelines prepared by Forome Project: https://github.com/ForomePlatform
   For now, this is probably the most complicated part of working with AnFiSA.
   In case of any issues, don't hesitate to contact members of the AnFiSA team directly.
#. Run AnFiSA and ensure that your data are available.
#. Open your data set and select **Filter Refiner** or **Decision Tree** mode.
    #. To use build-in filtering, just select and apply an appropriate filtering preset.
    #. To use custom filtering, create filter chain or decision tree from individual filters.
#. Create, name, and save a new derived dataset containing variants, satisfying the filtering criteria
#. Open created derived dataset and review resulting variations.
#. After the variations set becomes small enough, the filtering functions for complex events (like compound heterozygosity) will be available.
#. If needed, continue applying filters/decision trees, until you get a set of variations with reasonable size,
   which can be reviewed manually.
#. Review, tag, and create the user curation notes for variants in derived dataset
#. Export filtered and curated variants as a Microsoft Excel or CSV file.

Examples of both phenotype-based and genotype-based analysis are here: :ref:`analysis_examples`

For detailed review of the AnFiSA capabilities start from :ref:`intro`

:ref:`toc`