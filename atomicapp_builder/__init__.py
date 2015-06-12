# -*- coding: utf-8 -*-

import logging
import sys

file_handler = logging.FileHandler('atomicapp-builder.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))


def set_logging(level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.handlers = []
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(file_handler)


set_logging()
