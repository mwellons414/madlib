import time, re, os, subprocess 

class PSQLError(Exception):
    def __init__(self, returnMsg):
        self.returnMsg = returnMsg
    def __str__(self):
        return "psql failed with error %s." % self.returnMsg
    
def parseConnectionStr(connectionStr):
    """Parse connection strings of the form
    <tt>[username[/password]@][hostname][:port][/database][:schema]</tt>

    Separation characters (/@:) and the backslash (\) need to be escaped.
    @returns A tuple (username, password, hostname, port, database). Fields not
    specified will be None.
    """

    def unescape(string):
        """Unescape separation characters in connection strings, i.e., remove first
        backslash from "\/", "\@", "\:", and "\\".
        """
        if string is None:
            return None
        else:
            return re.sub(r'\\(?P<char>[/@:\\])', '\g<char>', string)

    match = re.search(
        r'((?P<user>([^/@:\\]|\\/|\\@|\\:|\\\\)+)' +
        r'(/(?P<password>([^/@:\\]|\\/|\\@|\\:|\\\\)*))?@)?' +
        r'(?P<host>([^/@:\\]|\\/|\\@|\\:|\\\\)+)?' +
        r'(:(?P<port>[0-9]+))?' + 
        r'(/(?P<database>([^/@:\\]|\\/|\\@|\\:|\\\\)+))?' + 
        r'(:(?P<schema>([^/@:\\]|\\/|\\@|\\:|\\\\)+))?', connectionStr)
    return (
        unescape(match.group('user')),
        unescape(match.group('password')),
        unescape(match.group('host')),
        match.group('port'),
        unescape(match.group('database')), 
        unescape(match.group('schema')))

"""
@brief Run SQL commands with psql and return output
@param psqlArgs: list of psql arguments
@param utility: run this sql in utility mode
@param stdinCmd: psql's stdin is piped from stdinCmd
"""
def runSQL(sql, logusername = None, logpassword = None, loghostname = None, logport = None,
            logdatabase = None, psqlArgs = None, utility=False, stdinCmd=None, onErrorStop = True,
              isFile = False, source_path = '', Return = "stdout"):
    """Run SQL commands with psql and return output

       params:
           psqlArgs: list of psql arguments
           utility: run this sql in utility mode
           stdinCmd: psql's stdin is piped from stdinCmd
    """
#     if logusername is None: logusername = ""
#     if logpassword is None: logpassword = ""
#     if loghostname is None: loghostname = ""
#     if logport is None: logport = ""
#     if logdatabase is None: logdatabase = ""
    # See
    # http://petereisentraut.blogspot.com/2010/03/running-sql-scripts-with-psql.html
    # for valuable information on how to call psql
    if onErrorStop is True:
        cmdLine = ['psql', '-X', '-q', '-v', 'ON_ERROR_STOP=1']
    else:
        cmdLine = ['psql', '-X', '-q', '-v', 'ON_ERROR_STOP=off']
    if loghostname is not None:
        cmdLine.extend(['-h', loghostname])
    if logport is not None:
        cmdLine.extend(['-p', str(logport)])
    if logdatabase is not None:
        cmdLine.extend(['-d', logdatabase])
    if logusername is not None:
        cmdLine.extend(['-U', logusername])
    
    if source_path:
        subprocess.call('source ' + source_path, shell = True)
        
    if psqlArgs:
        cmdLine.extend(psqlArgs)

    environ = dict(os.environ)
    if logpassword:
        environ['PGPASSWORD'] = logpassword
    
    if utility:
        environ['PGOPTIONS'] = '--client-min-messages=error  -c gp_session_role=utility'
    else:
        environ['PGOPTIONS'] = '--client-min-messages=error'
    
    if isFile:
        cmdLine.extend(['-f',"'" + sql + "'"])
        psql_cmd = ' '.join(cmdLine)
        subprocess.check_call(psql_cmd, shell = True)

    else:
        if stdinCmd:
            cmdLine.extend(['-c', "'" + sql + "'"])
            psqlCmd = ' '.join(cmdLine)
            stdinProcess = subprocess.Popen(stdinCmd, shell=True, stdout=subprocess.PIPE)
            psqlProcess = subprocess.Popen(psqlCmd, env = environ, shell=True, 
                stdin=stdinProcess.stdout, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
            (stdoutdata, stderrdata) = psqlProcess.communicate()
 
        else:
            psqlProcess = subprocess.Popen(cmdLine, env = environ,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (stdoutdata, stderrdata) = psqlProcess.communicate(sql)

        if psqlProcess.returncode != 0:
            print 'ERROR IN ', sql
            print 'Connection INFO ', logusername, logpassword\
                , loghostname, logport, logdatabase
            raise PSQLError(stderrdata)
    
        # Strip trailing newline character
        if stdoutdata[-1:] == '\n':
            stdoutdata = stdoutdata[:-1]
        if Return == "all":
            return str(stdoutdata) + str(stderrdata)
        else:
            return stdoutdata
        
def getDataDir(logusername = None, logpassword = None, loghostname = None
        , logport = None, logdatabase = None):
    """Get the master directory of gpdb."""

    return runSQL('''SELECT current_setting('data_directory')'''\
        , logusername, logpassword, loghostname, logport, logdatabase,
        ['--no-align', '--tuples-only'])

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
    
    @property
    def elapsed(self):
        return self.end - self.start
