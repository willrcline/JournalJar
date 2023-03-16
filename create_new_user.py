import pandas as pd
from drive_functions import uploadFile, shareFile
from msg_functions import welcome, initiate_confirmation
from datetime import datetime
import time
import numpy as np
import os
from client_data_functions import *
import config
# import s3fs
import boto3
# os.chdir(config.project_working_directory)
cwd = os.getcwd()
client_data_path = config.client_data_path

aws_access_key_id= config.aws_access_key_id
aws_secret_access_key= config.aws_secret_access_key

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
twilio_phone = config.twilio_phone
client = Client(config.twilio_account_sid, config.twilio_auth_token)


#creates a new row in the database with email, phone, and nickname. Called after form is submitted and before payment is completed
def auth_data(email, nickname):

    client_data = get_client_data()

    #prevent duplicates by using the same row if one is already made for that email (they submitted the form multiple times)
    try:
        row = client_data[client_data.email == email].reset_index()
        #Replace value in an entry
        client_data.loc[client_data.email == email ,'nickname']=nickname

        #test
        print('form data function has been performed to add data to an existing row with nickname:', row['nickname'][0], ' and email: ', row['email'][0])

    except: #if no current row with that email:
        #dynamically get column values for new row. Make sure the order of your values corresponds to the order in client_data
        #['nickname', 'phone', 'email', 'account_active', 'sign_up_date', 'stripe_customer_id','file_id', 'doc_link', 'time_zone', 'mq_time', 'eq_time','wants_responses_flag...'
        necessary_col_values = [nickname, np.nan, email, 'n']
        num_null_cols = len(client_data.columns) - len(necessary_col_values)
        all_col_values = necessary_col_values
        for i in range(num_null_cols):
            all_col_values.append(np.nan)
        #concat new row to client_data
        client_data = pd.concat([client_data,
                                pd.DataFrame([all_col_values], columns=client_data.columns)],
                                ignore_index=True)
    
        #DEPRECATED. NO LONGER HAVE PHONE AT THIS STAGE
        #send them a text
        # initiate_confirmation(nickname, phone)

        #test
        print('form data function has been performed to create a new row')

    #export
    put_client_data(client_data)


#requires a row that already has email and nickname. 
def create_new_user(email, phone, nickname):
    client_data = get_client_data()

    #dynamically get column values for new row. Make sure the order of your values corresponds to the order in client_data
    #['nickname', 'phone', 'email', 'account_active', 'sign_up_date', 'stripe_customer_id','file_id', 'doc_link', 'time_zone', 'mq_time', 'eq_time','wants_responses_flag...'
    necessary_col_values = [nickname, phone, email, 'y']
    num_null_cols = len(client_data.columns) - len(necessary_col_values)
    all_col_values = necessary_col_values
    for i in range(num_null_cols):
        all_col_values.append(np.nan)

    #concat new row to client_data
    client_data = pd.concat([client_data,
                            pd.DataFrame([all_col_values], columns=client_data.columns)],
                            ignore_index=True)

    # put_client_data(client_data)
    # client_data = get_client_data()

    #add values
    # sign_up date
    now=datetime.today()
    date_str = now.strftime("%m/%d/%y")
    client_data.loc[client_data.email == email ,'sign_up_date']=date_str
    client_data.loc[(client_data.email == email), ('phone')] = int(phone)
    client_data.loc[(client_data.email == email), ('nickname')] = nickname
    client_data.loc[(client_data.email == email), ('account_active')] = 'y'
    #set certain things to 0 instead of np.nan
    client_data.loc[(client_data.email == email), ('morning_entry_streak')] = 0
    client_data.loc[(client_data.email == email), ('evening_entry_streak')] = 0

    client_data.drop_duplicates(inplace=True)

    put_client_data(client_data)

    row = client_data[client_data['email']==email].reset_index()

    print("attempting to upload file in sign_up function")
    #create blank doc and upload to drive
    uploadFile(row['nickname'][0], row['phone'][0], row['email'][0])
    time.sleep(2)

    #read back in client data now with a google doc link hopefully
    client_data = get_client_data()
    row = client_data[client_data['email']==email].reset_index()

    print("attempting to share file in sign_up function")
    #share file with new user's email
    shareFile(row['email'][0], row['file_id'][0])

    print("attempting to send welcome msg in sign_up function")
    #send welcome msg
    welcome(row['nickname'][0], row['phone'][0], row['doc_link'][0])