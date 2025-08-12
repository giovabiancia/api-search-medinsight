#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: barnabas
"""
from werkzeug.middleware.proxy_fix import ProxyFix
from api import create_app
import os

app = create_app()

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if __name__ == '__main__':
    # Forza porta 5005 in development
    port = int(os.environ.get('PORT', 5005))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('ENV', 'LOCAL') != 'PRODUCTION'
    
    print(f"🚀 Avvio server su {host}:{port}")
    app.run(host=host, port=port, debug=debug)