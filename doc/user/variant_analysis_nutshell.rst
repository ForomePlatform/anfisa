.. _analysis_nutshell:

*******************************
Variant analysis in a nutshell
*******************************

The very brief instruction of installation and usage of AnFiSA.

#. Install AnFiSA via docker compose: https://github.com/ForomePlatform/deploy/blob/main/docker-compose/README.md
#. To analyse your own data use data processing pipelines prepared by Forome Project: https://github.com/ForomePlatform
   For now this is probably the most complicated part of working with AnFiSA.
   In case of any issues don't hesitate to contact members of AnFiSA team directly.
#. Run AnFiSA and ensure that your data are available
#. Open your data set and select **Filter Refiner** of **Decision Tree** mode
    #. To use build-in filtering, just select and apply an appropriate filtering preset
    #. To use custom filtering, create your own filter chain or decision tree
#. Create, name and save a new derived dataset containing variants satisfying the filtering
#. Open created derived dataset and review resulting variations
#. If needed, continue applying filters/decision trees, until you get set of variations with reasonable size,
   which can be reviewed manually.
#. Review, tag and create the user curation notes for variants in derived dataset
#. Export filtered and curated variants as a Microsoft Excel or CSV file.

Example of both phenotype-based and genotype-based analysis are here: :ref:`analysis_examples`

For detailed review of AnFiSA capabilities start from :ref:`intro`

:ref:`toc`