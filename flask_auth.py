from email import message
from operator import neg
import os
import time
# from turtle import update
import requests
from flask import Flask, request, redirect, render_template, url_for, session, jsonify, json
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
from threading import Timer
import numpy as np
import pandas as pd
import time
import sys
from drive_functions import *
from journal_doc_functions import *
from time_functions import to_utc
from msg_functions import *
from client_data_functions import *
from create_new_user import create_new_user, auth_data
from flask import Blueprint
import random
import config
# import s3fs
import boto3
# os.chdir(config.project_working_directory)
cwd = os.getcwd()

auth_blueprint = Blueprint('auth_blueprint', __name__)

client_data_path = config.client_data_path

aws_access_key_id= config.aws_access_key_id
aws_secret_access_key= config.aws_secret_access_key
#Creating Session With Boto3.
boto3_session = boto3.Session(
aws_access_key_id=aws_access_key_id,
aws_secret_access_key=aws_secret_access_key
)

flask_oauth = None
def init_flask_oauth(flask_app):
    global flask_oauth
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    flask_oauth = OAuth(flask_app)
    flask_oauth.register(
        name='google',
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

@auth_blueprint.route('/')
def index():
    redirect_uri = url_for('auth_blueprint.auth', _external=True)
    return flask_oauth.google.authorize_redirect("https://app.journaljar.io/auth")

@auth_blueprint.route('/sign_up')
def sign_up():
    return render_template('sign_up.html', stripe_pk_key=config.stripe_pk_key)

@auth_blueprint.route('/successful_sign_up')
def successful_sign_up():
    session.clear()
    session.pop('user', None)
    return render_template("successful_sign_up.html")

@auth_blueprint.route('/sign_in')
def sign_in():
    redirect_uri = url_for('auth', _external=True)
    return flask_oauth.google.authorize_redirect(redirect_uri)

@auth_blueprint.route('/auth')
def auth():
    token = flask_oauth.google.authorize_access_token()
    user = token.get('userinfo')
    session['user'] = user
    print(session['user'])

    #read in client data from database and match on email
    client_data = get_client_data()

    if user['email'] in list(pd.Series(client_data['email']).values):
        print('Someone whose email is already in client database authenticates: ', user['email'])
        # return redirect('/portal')
        row = client_data[client_data['email']==session['user']['email']].reset_index()
        if row['account_active'][0] == 'y':
            print('Existing user ', user['email'], 'authenticates')
            return redirect('/portal')
        else:
            print('New user, who has submitted a form before,', user['email'], 'authenticates')
            return redirect('/sign_up')

    else: #No email in DB; Presumably a new sign_up:
        print('New user', user['email'], 'authenticates. New sign_up function being called.')
        auth_data(session['user']['email'], session['user']['given_name'])
        return redirect('/sign_up')

@auth_blueprint.route('/sign_out')
def sign_out():
    #clears session for the user
    session.clear()
    session.pop('user', None)
    return redirect('/')
