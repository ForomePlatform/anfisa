CSV_FILE        = "/data/store/szubarev/Downloads/variant_summary.txt.gz"
XML_FILE        = "/data/store/szubarev/Downloads/ClinVarFullRelease_00-latest.xml.gz"

HOST            = 'localhost'
DBMS            = 'MySQL'
PORT            = 3306
USER            = "hgmd"
PASSWORD        = "hgmd"
DATABASE        = "clinvar_new"
TABLE_SUB       = "CV_Submitters"
TABLE_SIG       = "ClinVar2Sub_Sig"
TABLE_VAR       = "variant_summary"

COLUMN_SUB      = ( "SubmitterID",
                    "SubmitterName"
                    )
TYPE_SUB        = ( 'INT',
                    'TEXT CHARACTER SET utf8'
                    )
COLUMN_SIG      = ( "SubmitterID",
                    "RCVaccession",
                    'ClinicalSignificance'
                    )
TYPE_SIG        = ( 'INT',
                    'varchar(12)',
                    'varchar(60)'
                    )
COLUMN_VAR      = ( '#AlleleID',
                    'Type',
                    'Name',
                    'GeneID',
                    'GeneSymbol',
                    'HGNC_ID',
                    'ClinicalSignificance',
                    'ClinSigSimple',
                    'LastEvaluated',
                    'RS# (dbSNP)',
                    'nsv/esv (dbVar)',
                    'RCVaccession',
                    'PhenotypeIDS',
                    'PhenotypeList',
                    'Origin',
                    'OriginSimple',
                    'Assembly',
                    'ChromosomeAccession',
                    'Chromosome',
                    'Start',
                    'Stop',
                    'ReferenceAllele',
                    'AlternateAllele',
                    'Cytogenetic',
                    'ReviewStatus',
                    'NumberSubmitters',
                    'Guidelines',
                    'TestedInGTR',
                    'OtherIDs',
                    'SubmitterCategories',
                    'VariationID'
                    )
TYPE_VAR        = ( 'int(11) DEFAULT NULL',
                    'text',
                    'text',
                    'int(11) DEFAULT NULL',
                    'text',
                    'text',
                    'text',
                    'int(11) DEFAULT NULL',
                    'text',
                    'int(11) DEFAULT NULL',
                    'text',
                    'text',
                    'text',
                    'text',
                    'text',
                    'text',
                    'text',
                    'text',
                    'varchar(12) DEFAULT NULL',
                    'int(11) DEFAULT NULL',
                    'int(11) DEFAULT NULL',
                    'text',
                    'text',
                    'text',
                    'text',
                    'int(11) DEFAULT NULL',
                    'text',
                    'text',
                    'text',
                    'int(11) DEFAULT NULL',
                    'int(11) DEFAULT NULL'
                    )
# name, columns, unique, btree
INDEX_SUB       = ( ( "Index0", ( "SubmitterID", ), True, False ), )
INDEX_SIG       = ( ( "IndexUnic", ("RCVaccession", "SubmitterID", "ClinicalSignificance" ), True, False ),
                    ( "Index0", ("RCVaccession", "SubmitterID" ), False, False ),
                    ( "Index1", ( "SubmitterID", "RCVaccession"), False, False ) )
INDEX_VAR       = ( ( 'index1', ( '#AlleleID', ), False, True ), 
                    ( 'c_idx', ( 'Chromosome', ), False, True ), 
                    ( 'p_idx', ('Start', 'Stop'), False, True ),
                    ( 'Cs0_idx', ('ClinSigSimple', ), False, True ) )

BATCH_SIZE      = 1000

REFERENCE_PATHS = ( ( 'ClinVarAccession', 'Acc' ), # RCVaccession
                    )
ASSERTION_PATHS = ( ( 'ClinVarAccession', 'OrgID' ), # SubmitterID
                    ( 'ClinVarSubmissionID', 'submitter' ), # SubmitterName
                    'ClinicalSignificance/Description' # ClinicalSignificance
                    )

TABLES_MAP      = [ ( ( 1, 0 ), ( 1, 1 ) ),
                    ( ( 1, 0 ), ( 0, 0 ), ( 1, 2) )
                    ]

