# -*- coding: utf-8 -*-

import settings as const 
from settings import logger
from sendmail import sendmail
import deamon
import sys, time, os, datetime
from decimal import Decimal, getcontext
import socket
import helpers as h

class EWS(deamon.EWSoDS):
    """ Class of a Early Warning System that check space of all disks on localhost. """
    __percent_alarm_mode = False
    __value_alarm_mode = False
    __disk = None
    __capacity = None
    __available = None
    __used = None
    __percent_available = None
    __percent_available_str = None
    __host_name = socket.gethostname()
    __email_mark_file_path = None


    def calculations_disk_manager(self, _disk):
        """ Get and set all info about space on selected disk in iteration from daemon run. """

        def set_disk_info(_disk):
            """ Setting info about disk in private attrs: disk, capacity, available, used. """
            self.__disk_name = _disk
            self.__disk      = os.statvfs(_disk)
            self.__capacity  = self.__disk.f_bsize * self.__disk.f_blocks
            self.__available = self.__disk.f_bsize * self.__disk.f_bavail
            self.__used      = self.__disk.f_bsize * (self.__disk.f_blocks - self.__disk.f_bavail)
            getcontext().prec = 2
            self.__percent_available = ((self.__capacity - self.__used) / Decimal(self.__capacity))*100
            self.__percent_available_str = str( self.__percent_available ) + "%"
            self.__email_mark_file_path = const.MAIN_PWD+'/mail/' + self.__disk_name.replace('/','disk_')

        def set_ds_info():
            """ Setting information about available space for a given disk."""
            msg = "[Disk Space Available on %s] : %d percent free space - it is %s." % (
                self.__disk_name, 
                self.__percent_available,
                h.get_human_val_of_disk_space( self.__available) )
            logger.info(msg)

        set_disk_info(_disk)
        set_ds_info()

    def set_alarm_mode(self):
        """ Inform system which mode of alarm is on (all, for val, for %) """
        if const.ALARM_MODE == const.ALARM_MODE_LIST[0]:
            self.__value_alarm_mode = True
            self.__percent_alarm_mode = True
        elif const.ALARM_MODE == const.ALARM_MODE_LIST[1]:
            self.__value_alarm_mode = True
        elif const.ALARM_MODE == const.ALARM_MODE_LIST[2]:
            self.__percent_alarm_mode = True


    def alarm_manager(self):
        """ Manager of the alarm control that check space disk, setting log info and send email if it's necessary."""


        def __build_feed_back(alarm_name, percent=False, critical=False):
            msg = "%s ALARM!!!\n" % alarm_name
            msg += "\tPlease reduce disk space on %s server%s\n" % (self.__host_name, (" - NOW !!!" if critical else ".") )
            if percent:
                msg += "\tOn disk %s there is only %s of free space.\n" % (self.__disk_name, self.__percent_available_str) 
            else:
                msg += "\tOn disk %s there is only %s bajts of free space.\n" % (self.__disk_name, h.get_human_val_of_disk_space(self.__available))
            return msg

        def __check_percent_disk_space():
            alarm = 0
            body = ""
            if self.__percent_available <= const.CRITICAL_PERCENT_ALARM:
                alarm = 2
                body = __build_feed_back("CRITICAL PERCENT", True, True)
            elif self.__percent_available <= const.WARNING_PERCENT_ALARM:
                alarm = 1
                body = __build_feed_back("WARNING PERCENT", True)
            return alarm, body

        def __check_value_disk_space():
            alarm = 0
            body = ""
            if self.__available <= const.CRITICAL_VALUE_ALARM:
                alarm = 2
                body = __build_feed_back("CRITICAL VALUE", False, True)
            elif self.__available <= const.WARNING_VALUE_ALARM:
                alarm = 1
                body = __build_feed_back("WARNING VALUE")
            return alarm, body

        def __mail_sended_today():
            """ If alarm mode is True the system check last sended mail. 
            We don't want to make spam, so we send only one email per day for a unique disk!!!
            """
            if os.path.isfile(self.__email_mark_file_path):
                f = file(self.__email_mark_file_path, 'r')
            else:
                return False
            last_email_sent_date = datetime.datetime.strptime(f.read(), "%Y-%m-%d")
            f.close()
            today = datetime.date.today() 
            now_date = datetime.datetime(today.year,today.month,today.day)
            if last_email_sent_date == now_date:
                return True
            return False

        def __remove_email_mark():
            if self.__email_mark_file_path != None and os.path.isfile(self.__email_mark_file_path):
                os.remove(self.__email_mark_file_path);
                logger.debug( "Email mark removed." )

        def __create_email_mark():
            f = file(self.__email_mark_file_path, 'w+',0)
            f.write(str(datetime.date.today()))
            f.close()
            logger.debug( "Email mark created." )


        alarm = 0
        body = "[Disk Space Alarm detected on %s]\n" % self.__host_name
        if self.__percent_alarm_mode:
            alarm, msg = __check_percent_disk_space()
            body += msg
        if self.__value_alarm_mode:
            alarm, msg = __check_value_disk_space()
            body += msg;

        if alarm > 0:
            logger.info( body )
            if not __mail_sended_today():
                sent_status_ok = sendmail(alarm, body)
                if sent_status_ok:
                    __create_email_mark()
            else:
                logger.info( "Email already sent today." )
        else:
            __remove_email_mark()


    def run(self):
        self.set_alarm_mode();
        logger.info( "Daemon is going to run." )
        while True:
            for _disk in const.DISKS:
                self.calculations_disk_manager(_disk)
                self.alarm_manager()

            logger.info( "Daemon is going to sleep for a %d sec\n\n" % const.DAEMON_SLEEP)
            time.sleep(const.DAEMON_SLEEP)


if __name__ == "__main__":
    daemon = EWS()
    if len(sys.argv) == 2:
        user_mode = sys.argv[1]
        if 'start' == user_mode:
            daemon.start()
        elif 'stop' == user_mode:
            daemon.stop()
        #elif 'restart' == user_mode:
        #    daemon.restart()
        # improvements for realoading config in setting .. so its not enought right now !!! 
        #    and other problem is ealier sended email when was percent .. so after swap to value - no email !!!
        else:
            logger.info( "System lunched with unknown command. Instance is going down." )
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

