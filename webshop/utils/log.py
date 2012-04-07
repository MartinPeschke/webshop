# -*- coding: utf-8 -*-
import logging
from django.conf import settings 

def getlog():
    '''return us usage logger:
        usage:
            from utils import log
            log.getlog().debug("message")
    '''
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s]%(levelname)-8s"%(message)s"',
                        datefmt='%Y-%m-%d %a %H:%M:%S',
                        filemode='a+')

    logger = logging.getLogger()
    hdlr = logging.FileHandler(settings.LOG_FILE)
    formatter = logging.Formatter('[%(asctime)s]%(levelname)-8s"%(message)s"','%Y-%m-%d %a %H:%M:%S')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)

    return logger