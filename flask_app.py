from flask import Flask, render_template, redirect
from flask_sqlalchemy import flask_sqlalchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///tmp/test.db'