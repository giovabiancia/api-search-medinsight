#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author:        barnabas
@email:         barnabasaugustino@gmail.com
@github:        https://gitlab.com/barnabasaugustino/entry_requirements.git
@Domain name
@Hostname
@Description:   This document contains database utilities for entry_requirements project
"""
import os
import logging
import logging.config
from datetime import datetime


def configure_logger(name, log_path, handlers=['console', 'file']):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {'format': '%(asctime)s - %(name)s - %(levelname)s - '
                        '%(message)s - [in %(pathname)s:%(lineno)d]'},
            'short': {'format': '%(message)s'}
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_path,
                'maxBytes': 2097152,
                'backupCount': 20
            },
            'debug': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.StreamHandler'
            },
            'error': {
                'level': 'ERROR',
                'formatter': 'default',
                'class': 'logging.StreamHandler'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
        },
        'loggers': {
            'default': {
                'handlers': handlers,
                'level': 'DEBUG',
                'propagate': True
            },
            'info': {
                'handlers': handlers,
                'level': 'INFO',
                'propagate': True
            },
            'error': {
                'handlers': handlers,
                'level': 'ERROR',
                'propagate': True
            },
            'werkzeug': {'propagate': True},
        },
    })
    return logging.getLogger(name)


def create_log_directory():
    """
    Creates log file and directory
    """
    try:
        log_directory_path = os.path.join('./logs')
        os.makedirs(log_directory_path)
    except Exception as e:
        msg = f'eccezione: {e}'
        print(msg)
        # raise Exception(msg)
    return log_directory_path


def create_log_file(mode='a'):
    """
    :return:
    """
    # Create log directory
    log_directory_path = create_log_directory()
    # Create log file path
    log_file_path = os.path.join(log_directory_path, 'medinsights.log')
    with open(log_file_path, mode) as f:
        msg = f"Logfile start: {datetime.now()}"
        print(msg)
        f.write(msg)
    return log_file_path


log_file = create_log_file(mode='w')

if os.environ.get('ENV') in ['PRODUCTION', 'STAGING']:
    logger = configure_logger('error', log_file)
else:
    logger = configure_logger('info', log_file)

