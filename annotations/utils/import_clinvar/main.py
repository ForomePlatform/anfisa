#!/usr/bin/python2
# -*- coding: utf-8 -*-

'''
ClinVar Ingester
Analyze the XML and/or CSV files and then writing parsing data into the MySQL database
in the tables for Submittion Significance, for match of the Submitters Names and IDs and variant_summary table.
'''

import logging, time
import argparse,  sys

from annotations.utils.import_clinvar.defines import *
from annotations.utils.import_clinvar.parser import  XML_File, CSV_File
from annotations.utils.import_clinvar.table import Table

def main():
    # Init parser
    parser = argparse.ArgumentParser( prog = 'ClinVar Ingester', description = 
        "For parse XML file use -x flag.\nFor parse CVS file use -c flag.\nIf was parse XML file then use -s "\
        "flag for write Submittions Significance table and/or -n flag for write  Submitters Name match table.\n"\
        "If was parse CSV file then use -v flag for write variant_summary table.\nThere is no sense of using "\
        "last 3 flags without files parse. Flags can be combined.\nIf the database already contains writable "\
        "table, ClinVar Ingester will rename it with adding '_OLD' to an old name. If database already contains "\
        "an '_OLD' table, it will be dropped. If -d flag is used, existing writable table will be dropped instead "\
        "of renaming.\nDefault log file is written to $PWD with current date and '_clinvar.log' suffix in name.\n"\
        "Othe default variable values is stored in 'defines.py' file", formatter_class=argparse.RawTextHelpFormatter )
    # Arguments description
    parser.add_argument( "-x", help = "XML-file parsing flag", action = 'store_true' )
    parser.add_argument( "--xml-file", help = "Change path to XML file to import", default = XML_FILE )
    parser.add_argument( "-c", help = "CSV-file parsing flag", action = 'store_true' )
    parser.add_argument( "--csv-file", help = "Change path to CSV file to import", default = CSV_FILE )
    parser.add_argument( "-s", help = "Significance+ID+RCVAccession table write flag", action = 'store_true' )
    parser.add_argument( "--sig-table", help = "Change Significance+ID+RCVAccession table name", default = TABLE_SIG )
    parser.add_argument( "-n", help = "Submitter ID+Name table write flag", action = 'store_true' )
    parser.add_argument( "--name-table", help = "Change Submitter ID+Name table nane", default = TABLE_SUB )
    parser.add_argument( "-v", help = "variant_summary table write flag", action = 'store_true' )
    parser.add_argument( "--var_table", help = "Change variant_summary table name", default = TABLE_VAR )
    parser.add_argument( "-d", help = "Drop old tables, instead of rename", action = 'store_true' )
    parser.add_argument( "--log-file", "-l", help = "Change path to log file",
                        default = "{}_clinvar.log".format( time.strftime("%d_%m_%Y") ) )
    parser.add_argument( "--dbms", help = "DBMS type to import into", default = DBMS )
    parser.add_argument( "--database", help = "Change Database/Namespace", default = DATABASE )
    parser.add_argument( "--host", help = "DBMS host", default = HOST )
    parser.add_argument( "--port", type = int, help = "Change DBMS port", default =  PORT )
    parser.add_argument( "--user", help = "Change DBMS user", default = USER )
    parser.add_argument( "--password", help = "Change DBMS password", default = PASSWORD )
    # Parse arguments
    args = parser.parse_args( )
    # Init logging
    g_logger = logging.getLogger( 'clinvar' )
    g_handler = logging.FileHandler( args.log_file, mode='w', encoding='utf8' )
    g_formatter = logging.Formatter( '%(levelname)s@%(name)s:[%(asctime)s]>>> %(message)s' )
    g_handler.setFormatter( g_formatter )
    g_logger.addHandler( g_handler )
    g_logger.setLevel( logging.DEBUG )
    logger = logging.getLogger('clinvar.Main')
    # Greeting
    logger.info( "Hello." )
    logger.debug( args )#'{}\n\t{}'.format( args.xml_file, args.x_file ) )
    if args.x and ( args.s or args.n ) :
        # Processing of XML file
        logger.info( "Start ingesting XML file {}.".format( args.xml_file ) )
        # Init and get batch generator
        batch_gen = (XML_File( file_name = args.xml_file, ref_paths = REFERENCE_PATHS, asr_paths = ASSERTION_PATHS, 
                           tables_map = TABLES_MAP ).get_batch( BATCH_SIZE ) )
        if args.s :
            # Init database significance table
            sig = Table( host = args.host, database = args.database, port = args.port, user = args.user,
                    password = args.password, table = args.sig_table, dbms = args.dbms,
                    columns = COLUMN_SIG, types = TYPE_SIG, indexes = INDEX_SIG,
                    create = True, drop = args.d ) 
        # Significance insertion, submitter accumulation
        sub_dict = { } # unique sumitter dict
        ic = 0 # insert counter
        t = tb = time.time( ) # rate time, batch rate time
        for batch_list in batch_gen:
            # Dict and list accumulation
            insert_list = []
            for d in batch_list:
                if d[ 0 ][ 0 ] not in sub_dict:
                    sub_dict.update( { d[ 0 ][ 0 ]:d[ 0 ][ 1 ] } )
                elif sub_dict[ d[ 0 ][ 0 ] ] != d[ 0 ][ 1 ] :
                    if sub_dict[ d[ 0 ][ 0 ] ] is None :
                        sub_dict[ d[ 0 ][ 0 ] ] = d[ 0 ][ 1 ]
                    elif d[ 0 ][ 1 ] :
                        logger.debug( 'Name {} for {} known as {}.'.
                                        format( d[ 0 ][ 1 ], d[ 0 ][ 0 ], sub_dict[ d[ 0 ][ 0 ] ] )
                                    )
                insert_list += [ d [ 1 ] ]
            if args.s :
                # Data base insertion
                ic += sig.insert( insert_list ) 
                logger.debug( '{}; {}'.format( insert_list[ 0 ], len(insert_list) ) )
                logger.info( 'Significance = {}; Batch Rate = {};  General rate = {}.'.
                            format( ic, len( insert_list ) / ( time.time( ) - tb ), 
                                    ic / ( time.time( ) - t ) )
                        )
            tb = time.time( )
        if args.n :
            # Init database submitters table
            sub = Table( host = args.host, database = args.database, port = args.port, user = args.user,
                    password = args.password, table = args.name_table, dbms = args.dbms,
                    columns = COLUMN_SUB, types = TYPE_SUB, indexes = INDEX_SUB,
                    create = True, drop = args.d )
            # Submitter insertion
            sub_list = [ ] # unique submitter list
            ic = 0 # insert counter
            lt = tb = time.time( ) # rate time, batch rate time
            for sid in sub_dict :
                sub_list += [ ( sid, sub_dict[ sid ] ) ]
                if len( sub_list ) >= BATCH_SIZE :
                    # Data base insertion
                    ic += sub.insert( sub_list ) 
                    logger.debug( sub_list[ 0 ] )
                    logger.info( 'Submitters = {}; Batch Rate = {};  General rate = {}.'.
                                format( ic, len( sub_list ) / ( time.time( ) - tb ),
                                    ic / ( time.time( ) - lt ) )
                                )
                    del sub_list[ : ]
                    tb = time.time( )
            ic += sub.insert( sub_list )
            logger.debug( sub_list[ 0 ] )
            logger.info( 'Submitters = {}; Batch Rate = {};  General rate = {}.'.
                        format( ic, len( sub_list ) / ( time.time( ) - tb ),
                                        ic / ( time.time( ) - lt ) )
                        )
        logger.info( "Ingested {} in {}.".format( args.xml_file, time.time( ) - t ) )
    if args.c and args.v :
        # Processing of CSV file
        logger.info( "Start ingest CSV file {}.".format( args.csv_file ) )
        # Init and get batch generator
        batch_gen = CSV_File( args.csv_file ).get_batch( BATCH_SIZE )
        # Init database submissions table
        var = Table( host = args.host, database = args.database, port = args.port, user = args.user,
                    password = args.password, table = args.var_table, dbms = args.dbms,
                    columns = COLUMN_VAR, types = TYPE_VAR, indexes = INDEX_VAR,
                    create = True, drop = args.d )
        # Submission insertion
        ic = 0 # insert counter
        t = tb = time.time( ) # rate time, batch rate time
        for batch_list in batch_gen :
            # Data base insertion
            ic += var.insert( batch_list )
            logger.debug( batch_list[ 0 ] )
            logger.info( 'Submissions = {}; Batch Rate = {};  General rate = {}.'.
                            format( ic, len( batch_list ) / ( time.time( ) - tb ), 
                                    ic / ( time.time( ) - t ) )
                        )
            tb = time.time( )
        logger.info( "Ingested {} in {}.".format( args.csv_file, time.time( ) - t ) )
    # Farewell
    logger.info( "Bye bye." )


if __name__ == '__main__' :
    main()
