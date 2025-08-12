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
            try:
                self.conn = psycopg2.connect(host=self.host, port=self.port, dbname=self.db_name, user=self.user,
                                             password=self.password)
                if self.conn:
                    self.db_connected = True
                    break
            except Exception as e:
                loggerManager.logger.warning(f"Connection attempt {i+1} failed: {e}")
                if i == 4:  # Last attempt
                    raise e
                time.sleep(.5)

        self.engine = create_engine(engine_str)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def close_conn(self):
        try:
            if self.conn and not self.conn.closed:
                self.conn.close()
        except Exception as e:
            loggerManager.logger.debug(f"Error closing connection: {e}")
        
        try:
            if self.engine:
                self.engine.dispose()
        except Exception as e:
            loggerManager.logger.debug(f"Error disposing engine: {e}")
        
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

    def execute_query(self, query, country='default'):
        """
        :Description: Execute only insert or update query commands
        :param query: str, query to be executed
        :param country: str, country identifier for database selection
        :return: Inserted or updated record
        """
        try:
            if query:
                # Use country-specific cursor if available, otherwise default
                cursor = getattr(g, f'cursor_{country}', g.cursor)
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
            # close connection
            if g.get("db_connected"):
                close_db_for_country(country)
                setattr(g, f'db_connected_{country}', False)
            if request.is_json:
                raise error_handlers.InvalidAPIUsage(message=err_msg, status_code=500)
            else:
                abort(err_msg)
        return self


def get_database_config(country):
    """Get database configuration for specific country"""
    databases = current_app.config.get('DATABASES', {})
    
    if country in databases:
        return databases[country]
    
    # Fallback to Italy configuration for default
    return {
        'host': os.environ.get('IT_DB_HOST') if os.environ.get('IT_DB_HOST') else config.get('IT_DB_HOST'),
        'port': os.environ.get('IT_DB_PORT') if os.environ.get('IT_DB_PORT') else config.get('IT_DB_PORT'),
        'db_name': os.environ.get('IT_DB_NAME') if os.environ.get('IT_DB_NAME') else config.get('IT_DB_NAME'),
        'user': os.environ.get('IT_DB_USER') if os.environ.get('IT_DB_USER') else config.get('IT_DB_USER'),
        'password': os.environ.get('IT_DB_PASSWORD') if os.environ.get('IT_DB_PASSWORD') else config.get('IT_DB_PASSWORD')
    }


def connect_db_for_country(country='default'):
    """Connect to database for specific country"""
    db_config = get_database_config(country)
    
    pg = DbInitializePostgres(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        db_name=db_config['db_name']
    )
    pg.connect_db()
    
    # Store connections with country-specific names
    setattr(g, f'engine_{country}', pg.engine)
    setattr(g, f'conn_{country}', pg.conn)
    setattr(g, f'cursor_{country}', pg.cursor)
    setattr(g, f'db_connected_{country}', True)
    
    return pg.engine, pg.conn, pg.cursor


def connect_db():
    """Returns engine, connector and cursor for default database (backward compatibility)"""
    return connect_db_for_country('default')


def close_db_for_country(country='default'):
    """Close database connection for specific country"""
    engine = getattr(g, f'engine_{country}', None)
    conn = getattr(g, f'conn_{country}', None)
    cursor = getattr(g, f'cursor_{country}', None)
    
    try:
        if cursor and not cursor.closed:
            cursor.close()
    except Exception as e:
        loggerManager.logger.debug(f"Error closing cursor for {country}: {e}")
    
    try:
        if conn and not conn.closed:
            conn.commit()
            conn.close()
    except Exception as e:
        loggerManager.logger.debug(f"Error closing connection for {country}: {e}")
    
    try:
        if engine:
            engine.dispose()
    except Exception as e:
        loggerManager.logger.debug(f"Error disposing engine for {country}: {e}")


def close_db(engine, connector, cursor):
    """Close database and dispose engine (backward compatibility)"""
    try:
        if cursor and not cursor.closed:
            cursor.close()
    except Exception as e:
        loggerManager.logger.debug(f"Error closing cursor: {e}")
    
    try:
        if connector and not connector.closed:
            connector.commit()
            connector.close()
    except Exception as e:
        loggerManager.logger.debug(f"Error closing connector: {e}")
    
    try:
        if engine:
            engine.dispose()
    except Exception as e:
        loggerManager.logger.debug(f"Error disposing engine: {e}")
    
    return


def init_db():
    # Instantiate DbInitializePostgres
    # Use Italy configuration for initialization
    host = os.environ.get('IT_DB_HOST') if os.environ.get('IT_DB_HOST') else config.get('IT_DB_HOST')
    port = os.environ.get('IT_DB_PORT') if os.environ.get('IT_DB_PORT') else config.get('IT_DB_PORT')
    db_name = os.environ.get('IT_DB_NAME') if os.environ.get('IT_DB_NAME') else config.get('IT_DB_NAME')
    user = os.environ.get('IT_DB_USER') if os.environ.get('IT_DB_USER') else config.get('IT_DB_USER')
    password = os.environ.get('IT_DB_PASSWORD') if os.environ.get('IT_DB_PASSWORD') else config.get('IT_DB_PASSWORD')

    pg = DbInitializePostgres(host=host, port=port, user=user, password=password, db_name=db_name)
    pg.create_tables()


if __name__ == '__main__':
    print('Initializing the database started.')
    init_db()
    print('Initialized the database.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    parameters: str, country_code iso_alpha_3 describing a country
    server: str, database server to which we want to create a database
    :return:
    """
    click.echo('Initializing the database started.')
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)