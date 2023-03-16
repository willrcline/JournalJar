# from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
import io
import httplib2
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client as googleClient
import pandas as pd
import numpy as np
from os.path import exists
import os
import time
from datetime import datetime
import config
import boto3
from client_data_functions import *
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
# os.chdir(config.project_working_directory)
cwd = os.getcwd()
now=datetime.today()
date_str = now.strftime("%m/%d/%y")
client_data_path = config.client_data_path

twilio_phone = config.twilio_phone
client = Client(config.twilio_account_sid, config.twilio_auth_token)

aws_access_key_id= config.aws_access_key_id
aws_secret_access_key= config.aws_secret_access_key

CLIENTID = config.g_drive_CLIENTID
CLIENTSECRET = config.g_drive_CLIENTSECRET
REFRESHTOKEN = config.g_drive_REFRESHTOKEN

file_id = "1nk6Vw6lqbLR-WsqUd-cO7CihANnIFFAD"

credentials = googleClient.OAuth2Credentials(
    access_token=None,  # set access_token to None since we use a refresh token
    client_id=CLIENTID,
    client_secret=CLIENTSECRET,
    refresh_token=REFRESHTOKEN,
    token_expiry=None,
    token_uri=GOOGLE_TOKEN_URI,
    user_agent=None,
    revoke_uri=GOOGLE_REVOKE_URI)


def uploadFile(nickname, phone, email):
    client_data = get_client_data()
    row = client_data[client_data['email']==email].reset_index()
    file_name = nickname + "\'s" + " Benji Journal " + str(phone)
    file_path = '/tmp/' + file_name + '.txt'
    journal_doc_aws_key = config.aws_root_folder + '/' + config.journal_folder + '/' + file_name
    folder_id = config.g_drive_folder_id

    #don't execute if there is already a doc for this person (reset their file_id to nan in the datatable if already populated)
    if isinstance(row['file_id'][0], str):
        print('Already a file created for this person. (Reset their file_id to nan in the datatable if already populated)')
    else:
        # If there is not yet a journal for the person_create a blank one to have something to upload
        # check if file exists
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(config.aws_bucket)
        objs = list(bucket.objects.filter(Prefix=journal_doc_aws_key))

        # if file doesnt exist:
        if(len(objs)==0):
            boto3_session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            s3 = boto3_session.resource('s3')
            object = s3.Object(config.aws_bucket, journal_doc_aws_key)
            object.put(Body='')

        credentials.refresh(httplib2.Http())  # refresh the access token (optional)
        drive_service = build('drive', 'v3', http = credentials.authorize(httplib2.Http()))

        #download the file to /tmp/
        s3_client = boto3.resource('s3')
        s3_client.meta.client.download_file(config.aws_bucket, journal_doc_aws_key, file_path)

        file_metadata = {
            'name': file_name,
            "parents": [folder_id],
            'mimeType': 'text/plain'
            }
        media = MediaFileUpload(
            file_path,
            mimetype='text/plain',
            resumable=True
            )
        print("media file upload")

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
            ).execute()

        print("drive service file created")

        #add file_id of new google doc to the client data table
        file_id = file.get('id')
        doc_link = 'https://drive.google.com/file/d/' + file_id
        # client_data = get_client_data()
        client_data.loc[(client_data.email == email), ('file_id')] = file_id
        client_data.loc[(client_data.email == email), ('doc_link')] = doc_link
        put_client_data(client_data)

        # msg = client.messages.create(
        #             body= "client_data putted.",
        #             from_=twilio_phone,
        #             to='+12058079007'
        #         )

        print('Doc Link: ' + doc_link)
        print ('File ID: ' + file_id)


def updateFile(nickname, phone, file_id):
    file_name = nickname + "\'s" + " Benji Journal " + str(phone)
    file_path = '/tmp/' + file_name + '.txt'
    journal_doc_aws_key = config.aws_root_folder + '/' + config.journal_folder + '/' + file_name
    folder_id = config.g_drive_folder_id

    #download the journal doc to /tmp/
    s3_client = boto3.resource('s3')
    s3_client.meta.client.download_file(config.aws_bucket, journal_doc_aws_key, file_path)

    credentials.refresh(httplib2.Http())  # refresh the access token (optional)
    drive_service = build('drive', 'v3', http = credentials.authorize(httplib2.Http()))

    media = MediaFileUpload(
        file_path,
        mimetype='text/plain',
        resumable=True
        )
    file = drive_service.files().update(
        fileId=file_id,
        media_body=media,
        fields='id'
        ).execute()
    print ('File ID: ' + file.get('id'))

# def backup_client_data():
#     credentials.refresh(httplib2.Http())  # refresh the access token (optional)
#     drive_service = build('drive', 'v3', http = credentials.authorize(httplib2.Http()))

#     file_id = '1PntgcNTL0oLH52HVqOnoOyrCPpYAtGbu'

#     media = MediaFileUpload(
#         client_data_path,
#         mimetype='text/csv',
#         resumable=True
#         )
#     file = drive_service.files().update(
#         fileId=file_id,
#         media_body=media,
#         fields='id'
#         ).execute()
#     print ('File ID: ' + file.get('id'))


def shareFile(email, file_id):
    credentials.refresh(httplib2.Http())  # refresh the access token (optional)
    drive_service = build('drive', 'v3', http = credentials.authorize(httplib2.Http()))

    request_body = {
        'role': 'reader',
        'type': 'user',
        'emailAddress': email
    }
    response_permission = drive_service.permissions().create(
        fileId=file_id,
        body=request_body
        ).execute()
    print(response_permission)