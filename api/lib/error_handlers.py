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

from flask import current_app, g, request, jsonify
from api.lib import database_manager


class InvalidAPIUsage(Exception):
    def __init__(self, message=None, status_code=400, payload=None):
        super().__init__()
        """Invalid API usage object"""
        self.message = message
        self.status_code = status_code
        self.payload = payload
        # Disconnect from db
        if g.get("db_connected"):
            database_manager.close_db(g.engine, g.conn, g.cursor)
            g.db_connected = False

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

