
from tinctest.lib import PSQL
from gppylib.commands.base import Command
import os

import tinctest

class PSQL1 (PSQL):
    """
    This is a wrapper for running sql command.
    We add psql_options in this subclass.
    """
    def __init__(self, sql_file = None, sql_cmd = None, dbname = None, username = None, password = None,
                 PGOPTIONS = None, psql_options = None, host = None, port = None, out_file = None, 
                 output_to_file=True):

        
        if dbname == None:
            dbname_option = ""
        else:
            dbname_option = "-d %s" % (dbname)
        if username == None:
            username_option = ""
        else:
            username_option = "-U %s" % (username)
        if password is None:
            PGPASSWORD = ""
        else:
            PGPASSWORD = password
        if PGOPTIONS == None:
            PGOPTIONS = ""
        else:
            PGOPTIONS = "PGOPTIONS='%s'" % PGOPTIONS
        if psql_options == None:
            psql_cmd_options = ""
        else:
            psql_cmd_options = psql_options
        if host == None:
            hostname_option = ""
        else:
            hostname_option = "-h %s" % (host)
        if port == None:
            port_option = ""
        else:
            port_option = "-p %s" % (port)

        if sql_file is not None:
            assert os.path.exists(sql_file)
            if out_file == None:
                out_file = sql_file.replace('.sql', '.out')
            if out_file[-2:] == '.t':
                out_file = out_file[:-2]

            cmd_str = '%s psql %s %s %s %s %s -a -f %s' \
                % (PGOPTIONS, psql_cmd_options, dbname_option, username_option, 
                        hostname_option, port_option, sql_file)

            if output_to_file:
                cmd_str = "%s &> %s" % (cmd_str, out_file)
        else:
            assert sql_cmd is not None
            cmd_str = "%s %s psql %s %s %s %s %s -a -c \"%s\"" \
                      % (PGPASSWORD, PGOPTIONS,psql_cmd_options,dbname_option,
                         username_option,hostname_option,
                         port_option,sql_cmd)
        Command.__init__(self, 'run sql test', cmd_str)

    @staticmethod
    def run_sql_file(sql_file = None, dbname = None, username = None, password = None,
                     PGOPTIONS = None, psql_options = None, host = None, port = None, 
                     out_file = None, output_to_file=True):
        cmd = PSQL1(sql_file, None, dbname, username, password, PGOPTIONS, psql_options, 
                   host, port, out_file = out_file, output_to_file=output_to_file)
        tinctest.logger.info("Running sql file - %s" %cmd)
        cmd.run(validateAfter = False)
        result = cmd.get_results()
        tinctest.logger.info("Output - %s" %result)
        if result.rc != 0:
            return False
        return True

    @staticmethod
    def run_sql_command(sql_cmd = None, dbname = None, username = None, password = None,
                        PGOPTIONS = None, psql_options = None, host = None, port = None):
        cmd = PSQL1(None, sql_cmd, dbname, username, password, PGOPTIONS, psql_options, host, port)
        tinctest.logger.info("Running command - %s" %cmd)
        cmd.run(validateAfter = False)
        result = cmd.get_results()
        tinctest.logger.info("Output - %s" %result)
        return result.stdout

