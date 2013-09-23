# -*- coding: utf-8 -*-

import smtplib, sys
from smtplib import SMTPException
import datetime
from settings import logger
import settings as const
from email.MIMEText import MIMEText


def sendmail(alarm, body_msg, subject='EWSoDS detect low disk space !!!'):
    """ Sending mail through the smtp lib. """
    try:
        receiver = const.CRITICAL_EMAIL if alarm == 2 else const.WARNING_EMAIL
        smtpObj = smtplib.SMTP(const.SMTP_HOST, const.SMTP_PORT)
        message = MIMEText(body_msg)
        message['From'] = const.SMTP_SENDER
        message['To'] = receiver
        message['Subject'] = subject
        smtpObj.sendmail( message['From'], message['To'], message.as_string())
        logger.info( "Mail is just sended successfully." )
        return True
    except SMTPException, e:
        logger.error( "Unable to send email. SMTPException !!! see line below for details:\n" + e )
    except Exception, e:
        logger.critical( "Unable to send email. Exception !!! see line below for details:\n" + e )
    return False;

