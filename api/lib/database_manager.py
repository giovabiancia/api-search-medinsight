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

# External dependencies
import click
from flask import current_app, g, request, abort
from flask.cli import with_appcontext
import time
import os
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, text
from dotenv import dotenv_values
# Internal dependencies
from api.lib import error_handlers, util, loggerManager

config = dotenv_values(".env")

class DbInitializePostgres(object):
    def __init__(self, host=None, port=None, user=None, password=None, db_name=None):
        self.db_name = db_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.engine = self.conn = self.cursor = None
        self.db_connected = self.server_connected = False

    def connect_db_server(self):
        for i in range(5):
            self.conn = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password)
            if self.conn:
                self.server_connected = True
                break
            time.sleep(.5)

        self.conn.autocommit = True
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def connect_db(self):
        loggerManager.logger.debug(f"host: {self.host}")
        loggerManager.logger.debug(f"port: {self.port}")
        loggerManager.logger.debug(f"db name: {self.db_name}")
        loggerManager.logger.debug(f"user: {self.user}")
        loggerManager.logger.debug(f"password: {self.password}")
        engine_str = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"

        for i in range(5):
            self.conn = psycopg2.connect(host=self.host, port=self.port, dbname=self.db_name, user=self.user,
                                         password=self.password)
            if self.conn:
                self.db_connected = True
                break
            time.sleep(.5)

        self.engine = create_engine(engine_str)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def close_conn(self):
        self.conn.close()
        if self.engine:
            self.engine.dispose()
        return self

    def create_db(self):
        self.connect_db_server()
        self.cursor.execute(f'DROP DATABASE IF EXISTS {self.db_name}')
        self.cursor.execute(f'CREATE DATABASE {self.db_name}')
        self.close_conn()
        return self

    def create_tables(self):
        self.connect_db()
        queries = os.path.join('setup_tables.sql')
        with open(queries, 'r') as f:
            self.cursor.execute(f.read())
        self.close_conn()
        return self


class ExecuteQueries(DbInitializePostgres):
    def __init__(self):
        super(ExecuteQueries, self).__init__()
        self.query_result = None

    def execute_query(self, query, country_code=None):
        """
        :Description: Execute only insert or update query commands
        :param query: str, query to be executed
        :param country_code: str, country code (DE, IT) for multi-database support
        :return: Inserted or updated record
        """
        try:
            if query:
                # Use country-specific cursor if available, otherwise default cursor
                cursor = getattr(g, f'cursor_{country_code.lower()}', g.cursor) if country_code else g.cursor
                cursor.execute(query)
                self.query_result = cursor.fetchall()
                if len(self.query_result) == 1:
                    self.query_result = dict(self.query_result[0])
                elif len(self.query_result) > 1:
                    self.query_result = [dict(record) for record in self.query_result]
                else:
                    self.query_result = None

        except Exception as e:
            err_msg = f'Error in execute_query: {query}: {e}'
            loggerManager.logger.error(err_msg)
            err_msg = f'Server Error'
            # close connections
            close_all_db_connections()
            if request.is_json:
                raise error_handlers.InvalidAPIUsage(message=err_msg, status_code=500)
            else:
                abort(err_msg)
        return self


def get_db_config(country_code):
    """Get database configuration for specific country"""
    db_params = current_app.config.get('DATABASE_PARAMS', {})
    return db_params.get(country_code.upper(), {})


def connect_db(country_code=None):
    """Returns engine, connector and cursor for specific country"""
    if country_code:
        db_config = get_db_config(country_code)
        if not db_config:
            raise ValueError(f"Database configuration not found for country: {country_code}")
        
        host = db_config.get('host')
        port = db_config.get('port')
        db_name = db_config.get('db_name')
        user = db_config.get('user')
        password = db_config.get('password')
    else:
        # Fallback to legacy configuration
        host = os.environ.get('DATABASE_HOST') if os.environ.get('DATABASE_HOST') else config.get('DATABASE_HOST')
        port = os.environ.get('DATABASE_PORT') if os.environ.get('DATABASE_PORT') else config.get('DATABASE_PORT')
        db_name = os.environ.get('DB_NAME') if os.environ.get('DB_NAME') else config.get('DB_NAME')
        user = os.environ.get('DATABASE_USER') if os.environ.get('DATABASE_USER') else config.get('DATABASE_USER')
        password = os.environ.get('DATABASE_PASSWORD') if os.environ.get('DATABASE_PASSWORD') else config.get('DATABASE_PASSWORD')

    pg = DbInitializePostgres(host=host, port=port, user=user, password=password, db_name=db_name)
    pg.connect_db()
    return pg.engine, pg.conn, pg.cursor


def connect_all_country_dbs():
    """Connect to all configured country databases"""
    connections = {}
    try:
        db_params = current_app.config.get('DATABASE_PARAMS', {})
        for country_code in db_params.keys():
            try:
                engine, conn, cursor = connect_db(country_code)
                connections[country_code.lower()] = {
                    'engine': engine,
                    'conn': conn,
                    'cursor': cursor
                }
                loggerManager.logger.info(f"Connected to database for country: {country_code}")
            except Exception as e:
                loggerManager.logger.error(f"Failed to connect to database for country {country_code}: {e}")
                
    except Exception as e:
        loggerManager.logger.error(f"Error connecting to country databases: {e}")
    
    return connections


def close_db(engine, connector, cursor):
    """Close database and dispose engine"""
    try:
        cursor.close()
        connector.commit()
        connector.close()
        if engine:
            engine.dispose()
    except Exception as e:
        loggerManager.logger.error(f"Error closing database connection: {e}")


def close_all_db_connections():
    """Close all database connections"""
    try:
        # Close country-specific connections
        for country in ['de', 'it']:
            if hasattr(g, f'engine_{country}'):
                close_db(
                    getattr(g, f'engine_{country}'),
                    getattr(g, f'conn_{country}'),
                    getattr(g, f'cursor_{country}')
                )
                delattr(g, f'engine_{country}')
                delattr(g, f'conn_{country}')
                delattr(g, f'cursor_{country}')
        
        # Close default connection if exists
        if hasattr(g, 'engine'):
            close_db(g.engine, g.conn, g.cursor)
            
        g.db_connected = False
    except Exception as e:
        loggerManager.logger.error(f"Error closing all database connections: {e}")


def init_db():
    # Legacy function for backward compatibility
    host = os.environ.get('DATABASE_HOST') if os.environ.get('DATABASE_HOST') else config.get('DATABASE_HOST')
    port = os.environ.get('DATABASE_PORT') if os.environ.get('DATABASE_PORT') else config.get('DATABASE_PORT')
    db_name = os.environ.get('DB_NAME') if os.environ.get('DB_NAME') else config.get('DB_NAME')
    user = os.environ.get('DATABASE_USER') if os.environ.get('DATABASE_USER') else config.get('DATABASE_USER')
    password = os.environ.get('DATABASE_PASSWORD') if os.environ.get('DATABASE_PASSWORD') else config.get('DATABASE_PASSWORD')

    pg = DbInitializePostgres(host=host, port=port, user=user, password=password, db_name=db_name)
    pg.create_tables()


if __name__ == '__main__':
    print('Initializing the database started.')
    init_db()
    print('Initialized the database.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize database"""
    click.echo('Initializing the database started.')
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)