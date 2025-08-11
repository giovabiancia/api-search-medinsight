#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author:        barnabas
@email:         barnabasaugustino@gmail.com
@github:        https://gitlab.com/barnabasaugustino/entry_requirements.git
@Domain name
@Hostname
@Description:   Database manager semplificato per più paesi
"""

import click
from flask import current_app, g, request, abort
from flask.cli import with_appcontext
import time
import os
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
from dotenv import dotenv_values
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
        self.db_connected = False

    def connect_db(self):
        loggerManager.logger.debug(f"Connecting to: {self.host}:{self.port}/{self.db_name}")
        engine_str = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"

        for i in range(5):
            try:
                self.conn = psycopg2.connect(host=self.host, port=self.port, dbname=self.db_name, 
                                           user=self.user, password=self.password)
                if self.conn:
                    self.db_connected = True
                    break
            except:
                time.sleep(.5)

        if not self.db_connected:
            raise Exception(f"Cannot connect to database {self.db_name}")

        self.engine = create_engine(engine_str)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def close_conn(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
        return self

class ExecuteQueries(object):
    def __init__(self):
        self.query_result = None

    def execute_query(self, query):
        try:
            if query:
                g.cursor.execute(query)
                self.query_result = g.cursor.fetchall()
                if len(self.query_result) == 1:
                    self.query_result = dict(self.query_result[0])
                elif len(self.query_result) > 1:
                    self.query_result = [dict(record) for record in self.query_result]
                else:
                    self.query_result = None
        except Exception as e:
            err_msg = f'Error in execute_query: {e}'
            loggerManager.logger.error(err_msg)
            if request.is_json:
                raise error_handlers.InvalidAPIUsage(message="Server Error", status_code=500)
            else:
                abort(500)
        return self

def connect_db(country='IT'):
    """Connette al database del paese specificato"""
    from api.lib.config_manager import Configuration
    db_config = Configuration.get_db_config(country)
    
    pg = DbInitializePostgres(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        db_name=db_config['name']
    )
    pg.connect_db()
    return pg.engine, pg.conn, pg.cursor

def close_db(engine, connector, cursor):
    """Chiude connessione database"""
    if cursor:
        cursor.close()
    if connector:
        connector.commit()
        connector.close()
    if engine:
        engine.dispose()

def init_db():
    """Inizializza database per entrambi i paesi"""
    # Inizializza Germania
    try:
        from api.lib.config_manager import Configuration
        db_config = Configuration.get_db_config('DE')
        pg = DbInitializePostgres(**db_config)
        pg.connect_db()
        # Crea tabelle se necessario
        queries = os.path.join('setup_tables.sql')
        if os.path.exists(queries):
            with open(queries, 'r') as f:
                pg.cursor.execute(f.read())
        pg.close_conn()
        loggerManager.logger.info("Database Germania inizializzato")
    except Exception as e:
        loggerManager.logger.error(f"Errore inizializzazione DB Germania: {e}")

    # Inizializza Italia
    try:
        db_config = Configuration.get_db_config('IT')
        pg = DbInitializePostgres(**db_config)
        pg.connect_db()
        queries = os.path.join('setup_tables.sql')
        if os.path.exists(queries):
            with open(queries, 'r') as f:
                pg.cursor.execute(f.read())
        pg.close_conn()
        loggerManager.logger.info("Database Italia inizializzato")
    except Exception as e:
        loggerManager.logger.error(f"Errore inizializzazione DB Italia: {e}")

@click.command('init-db')
@with_appcontext
def init_db_command():
    click.echo('Inizializzazione database...')
    init_db()
    click.echo('Database inizializzati.')

def init_app(app):
    app.cli.add_command(init_db_command)