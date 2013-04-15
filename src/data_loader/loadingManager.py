#! /usr/bin/env python

"""
loadingManager.py

---
cmd : "./convertor.sh <data> <sql> <table> <desc>"
    - id : rf_madelon_train
      args :
          data : "http://archive.ics.uci.edu/ml/machine-learning-databases/madelon/MADELON/madelon_train.data"
          desc : "./desc/madelon.desc"
    - id : rf_madelon_test
      args :
          data : "http://archive.ics.uci.edu/ml/machine-learning-databases/madelon/MADELON/madelon_test.data"
          desc : "./desc/madelon_test.desc"
    - id : rf_isolet_train
      args :
          data : "http://archive.ics.uci.edu/ml/machine-learning-databases/isolet/isolet5.data.Z"
          desc : "./desc/isolet.desc"
    - id : rf_isolet_test
      args :
          data : "http://archive.ics.uci.edu/ml/machine-learning-databases/isolet/isolet1+2+3+4.data.Z"
          desc : "./desc/isolet_test.desc"

"""

import os
import sys
import yaml
import subprocess
import types
import re
import time
import urllib
from src.test_utils.get_dbsettings import get_dbsettings
import dbManager, run_sql

class loadingManager:
    """Manage loading"""
    # ----------------------------------------------------------------
    
    def __init__(self):
        """Load the config yaml"""
        source_file = sys.modules[self.__class__.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(source_file))
        self.__yamlPath = os.path.join(source_dir, "../../datasets/")
        self.testdbs_conf = get_dbsettings()
        self.__schema = self.testdbs_conf["schema_testing"]
        self.__sqlPath = os.path.join(self.__yamlPath, "sql")
        self.conf = yaml.load(open(self.__yamlPath + "config.yaml"))
        # self.testdbs_conf = analyticsTools.analyticsTools
        self.__log = {}

    # ----------------------------------------------------------------
        
    def __logInfo(self, id, attri, value):
        """Help log info of loading process."""
        if id not in self.__log:
            self.__log[id] = {}
        self.__log[id][attri] = value

    # ----------------------------------------------------------------
        
    def __getYamls(self, yaml_dict, root):
        """An assistant function called by __loadYaml."""
        yaml_list = []
        for key, value in yaml_dict.items():
            if isinstance(value, dict):
                yaml_list += self.__getYamls(value, root + key + '/')
            elif (value is None) or (value is True):
                yaml_list.append(root + key + '/tables.yaml')
        return yaml_list

    # ----------------------------------------------------------------
        
    def __loadYaml(self, modules=None):
        """Load from file."""
        yaml_list = self.__getYamls(self.conf, self.__yamlPath)
        if modules is not None:
            new_list = []
            for module in modules:
                for yaml in yaml_list:
                    if module in yaml and yaml not in new_list:
                        new_list.append(yaml)
            return new_list
        return yaml_list

    # ----------------------------------------------------------------
        
    def __convert(self, data_list, overwritten=False):
        """Convert dataset to sql format."""
        if data_list is None:
            sys.exit('No yamls found.')
        fail_list = []
        for yaml_path in data_list:
            if os.path.exists(yaml_path) is False:
                continue
            (root, _) = os.path.split(yaml_path)
            cfg = yaml.load(open(yaml_path))
            if not 'tables' in cfg:
                continue
            for table in cfg['tables']:
                if 'skip' in table and table['skip'] == 'all':
                    continue
                cmd = ""
                if 'cmd' in table:
                    cmd = table['cmd']
                else:
                    cmd = cfg['cmd']
                table_name = '.'.join([self.__schema, table['id']])
                outSQL = os.path.join(self.__yamlPath, 'sql', table['id'] + '.sql')
                if os.path.exists(outSQL + '.gz') is True and \
                        overwritten is False:
                    print "INFO : %s exists." % outSQL
                    continue
                try:
                    tags = re.compile('<\w*>').findall(cmd)
                    for tag in tags:
                        if tag == '<sql>':
                            cmd = cmd.replace(tag, outSQL)
                        elif tag == '<table>':
                            cmd = cmd.replace(tag, table_name)
                        else:
                            cmd = cmd.replace(tag,
                                            self.__smartDownload(
                                               table['args'][tag[1:-1]], table))
                    cwd = os.getcwd()
                    os.chdir(root)
                    start = time.time()
                    subprocess.check_call(cmd, shell=True)
                    self.__logInfo(table['id'], 'convert', time.time() - start)
                    os.chdir(cwd)

                    self.__logInfo(table['id'], 'size', os.path.getsize(outSQL))
                    subprocess.check_call('gzip -f %s' % outSQL, shell=True)
                    print 'INFO : Success Convert : %s' % table['id']
                except Exception as e:
                    fail_list.append(table['id'])
                    print str(e)
        print "FAILED CONVERT LIST:\n", fail_list

    # ----------------------------------------------------------------
        
    def __smartDownload(self, str, table):
        if str.startswith('http'):
            fileName = os.path.join(self.__yamlPath, 'download', str.split('/')[-1])

            if fileName.endswith('.gzip') or \
                    (fileName.endswith('.gz') and not
                        fileName.endswith('.tar.gz')) or \
                    fileName.endswith('.Z'):
                data_name = '.'.join(fileName.split('.')[:-1])
                if os.path.exists(data_name) is False:
                    web_file = urllib.urlopen(str)
                    local_file = open(fileName, 'w')
                    local_file.write(web_file.read())
                    web_file.close()
                    local_file.close()
                    subprocess.call('gunzip -f %s' % fileName, shell=True)
                return data_name

            elif os.path.exists(fileName) is False:
                start = time.time()
                web_file = urllib.urlopen(str)
                local_file = open(fileName, 'w')
                local_file.write(web_file.read())
                web_file.close()
                local_file.close()
                elapsed = (time.time() - start)
                self.__logInfo(table['id'], 'download', elapsed)
            return os.path.abspath(fileName)
        return str

    # ----------------------------------------------------------------
        
    def __load(self, db_manager, yaml_list, overload=False):
        """Load table into db."""
        fail_list = []
        for yaml_path in yaml_list:
            if os.path.exists(os.path.join(self.__yamlPath, yaml_path)) \
                    is False:
                continue
            yaml_content = yaml.load(open(os.path.join(self.__yamlPath, yaml_path)))
            if 'tables' in yaml_content:
                for table in yaml_content['tables']:
                    # if 'skip' in table and \
                    #         (table['skip'] == 'all' or (table['skip'] in kind)):
                    #     continue
                    table_name = '.'.join([self.__schema, table['id']])
                    outSQL = os.path.join(self.__yamlPath, 'sql', table['id'] + '.sql')
                    output = run_sql.runSQL("SELECT count(*) FROM %s" % table_name,
                                            psqlArgs=db_manager.getDBsqlArgs(),
                                            onErrorStop=False, Return="all")
                    #If table exists and no nedd to overload, skip this sql.
                    if output.find('not exist') < 0 and \
                            output.find('     0') < 0 and overload is False:
                        continue
                    elif output.find('     0') > 0 and overload is False:
                        fail_list.append(table['id'])
                        print "ERROR : Success create but copy failed : %s" % table['id']
                        continue
                    try:
                        start = time.time()
                        subprocess.check_call('gunzip -f %s.gz' % outSQL, shell=True)
                        run_sql.runSQL(outSQL, logport=str(db_manager.db_conf['port']),
                                      logdatabase=db_manager.db_conf['dbname'],
                                      onErrorStop=False, isFile=True,
                                      source_path=db_manager.getDBenv())
                        subprocess.check_call('gzip -f %s' % outSQL, shell=True)
                        self.__logInfo(table['id'], 'load', time.time() - start)
                        #Load additional sql file for table.
                        if 'sql' in table:
                            run_sql.runSQL(os.path.join(self.__yamlPath,
                                    os.path.dirname(yaml_path), table['sql']),
                                    logport=str(db_manager.db_conf['port']),
                                    logdatabase=db_manager.db_conf['dbname'],
                                    onErrorStop=False, isFile=True,
                                    source_path=db_manager.getDBenv())
                        print "INFO : Success Loaded : %s " % table['id']
                    except:
                        fail_list.append(table['id'])
                        print "ERROR : Fail Loaded : %s " % table['id']
            #Load additional sql file for algorithm.
            if 'sql' in yaml_content:
                run_sql.runSQL(os.path.join(self.__yamlPath,
                            os.path.dirname(yaml_path), yaml_content['sql']),
                            logport=str(db_manager.db_conf['port']),
                            logdatabase=db_manager.db_conf['dbname'],
                            onErrorStop=False, isFile=True,
                            source_path=db_manager.getDBenv())
        print "FAILED LOAD TABLES:\n", fail_list

    # ----------------------------------------------------------------
        
    def do(self, modules=None, overwritten=False, overload=False, initdb=False):
        """Read yaml files, download, unzip, convert and load"""
        yaml_list = self.__loadYaml(modules)
        self.__convert(yaml_list, overwritten)

        db_manager = dbManager.dbManager(self.testdbs_conf)
        # db_manager.start()

        if initdb is True:
            db_manager.initDB()

        self.__load(db_manager, yaml_list, overload)
        # db_manager.stop()
        total_time = 0.0
        for id, attris in self.__log.items():
            info = ''
            for key, value in attris.items():
                if key in ('load', 'convert', 'download'):
                    total_time += value
                info += key + ':' + str(value) + '\t'
            print id + '\t' + info
        print "Total Time Spent:", total_time

# ------------------------------------------------------------------------

def main():
    loading_manager = loadingManager()

    smart = False
    if os.environ.has_key("SMART"):
        value = os.environ.get("SMART").lower()
        if (value == "t" or value == "true" or
            value == "yes" or value == "y"):
            smart = True

    if smart:
        loading_manager.do(None, False, False, False)
    else:
        loading_manager.do(None, False, True, True)

# ------------------------------------------------------------------------
    
if __name__ == '__main__':
    main()
