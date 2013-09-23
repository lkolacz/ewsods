# -*- coding: utf-8 -*-

import os;
import subprocess;
import logging;
import ConfigParser

MAIN_PWD = os.getcwd()

#--------------------------------------------------------------------------------------------------

config = ConfigParser.ConfigParser()
config.read(MAIN_PWD+'/base.cfg')

#--------------------------------------------------------------------------------------------------
# daemon sleep
#--------------------------------------------------------------------------------------------------
DAEMON_SLEEP = config.getint("daemon sleep","days") * 24 * 60 * 60\
                    + config.getint("daemon sleep","hours") * 60 * 60\
                    + config.getint("daemon sleep","minutes") * 60\
                    + config.getint("daemon sleep","seconds")

#--------------------------------------------------------------------------------------------------
# pid 
#--------------------------------------------------------------------------------------------------
PATH_TO_APP_PID = MAIN_PWD + config.get("pid","sub_path")

#--------------------------------------------------------------------------------------------------
# logger
#--------------------------------------------------------------------------------------------------
logger = logging.getLogger( config.get("logger","name") )
formatter = logging.Formatter( config.get("logger","formatter", raw=True) )
hdlr = logging.FileHandler( MAIN_PWD + config.get("logger","subdir") )
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

if config.get("logger","level") == "debug":
    logger.setLevel(logging.DEBUG)
elif config.get("logger","level") == "info":
    logger.setLevel(logging.INFO)
elif config.get("logger","level") == "error":
    logger.setLevel(logging.ERROR)
elif config.get("logger","level") == "critical":
    logger.setLevel(logging.CRITICAL)
else:
    logger.setLevel(logging.INFO)

#--------------------------------------------------------------------------------------------------
# alarm mode
#--------------------------------------------------------------------------------------------------
ALARM_MODE_LIST = config.get("alarm mode","all_modes").split(",")
ALARM_MODE = config.get("alarm mode","mode")
df = subprocess.Popen(["df","-l"], stdout=subprocess.PIPE)
bg,com = df.communicate()
DISKS = filter(lambda x: x!=None, [ line.split()[5] if line.split() else None  for line in bg.split("\n")[1:]])

#--------------------------------------------------------------------------------------------------
# critical alarm
#--------------------------------------------------------------------------------------------------
CRITICAL_VALUE_ALARM = config.getint("critical alarm","value") #bajts
CRITICAL_PERCENT_ALARM = config.getint("critical alarm","percent") #%
CRITICAL_EMAIL = config.get("critical alarm","email")

#--------------------------------------------------------------------------------------------------
#warning alarm
#--------------------------------------------------------------------------------------------------
WARNING_VALUE_ALARM = config.getint("warning alarm","value") #bajts
WARNING_PERCENT_ALARM = config.getint("warning alarm","percent") #%
WARNING_EMAIL = config.get("warning alarm","email")

#--------------------------------------------------------------------------------------------------
# smtp
#--------------------------------------------------------------------------------------------------
SMTP_HOST = config.get("smtp","host")
SMTP_PORT = config.getint("smtp","port")
SMTP_SENDER = config.get("smtp","sender")

#--------------------------------------------------------------------------------------------------

