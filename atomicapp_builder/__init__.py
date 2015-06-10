# -*- coding: utf-8 -*-

import logging

def set_logging(level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.handlers = []
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

set_logging()
