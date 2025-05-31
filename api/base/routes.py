from flask import Flask, request, Blueprint, session, g

bp = Blueprint("base", __name__, url_prefix='', static_folder='static')