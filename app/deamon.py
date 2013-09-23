# -*- coding: utf-8 -*-

import sys, os, time, atexit, datetime
from settings import logger
from signal import SIGTERM
from settings import PATH_TO_APP_PID
 
class EWSoDS:
    """
    A generic Early Warning System of Disk Space class.
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self):
        self.pidfile = PATH_TO_APP_PID

    def daemonize(self):
        """ Register a daemon process """
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            logger.error("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            logger.error("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        """Removing pid file."""
        os.remove(self.pidfile)
 
    def start(self):
        """Start the daemon with checking is he already run"""
        try:
            pf = file(self.pidfile,'r')
            pid = pf.read().strip()
            pf.close()
        except IOError:
            pid = None
       
        if pid != None and os.path.exists("/proc/" + pid):
            message = "pidfile %s already exist. Daemon already running!!!\n" % self.pidfile
            logger.error( message )
            sys.exit(1)

        logger.debug( "EWSoDS daemon is going to star." )
        self.daemonize()
        self.run()
        logger.debug( "EWSoDS daemon has been started." )

 
    def stop(self):
        """Stop the daemon with checking is daemon already run"""
        # Get the pid from the pidfile
        logger.debug( "EWSoDS daemon is going to stop." )
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            logger.debug( "EWSoDS daemon check pid. [pidfile] : %s does not exist. Daemon not running?" % self.pidfile )
            return 

        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
 
    def restart(self):
        """Restart the daemon. First try to stop and then try to start"""
        logger.debug( "EWSoDS daemon is going to restart (stop, start)." )
        self.stop()
        self.start()
 
    def run(self):
        """Abstract  method to override."""
        pass

