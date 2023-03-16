import os
from twilio.rest import Client as twilioClient
import time
import pandas as pd
import numpy as np
import random
from datetime import datetime
from client_data_functions import *
import config
# import s3fs
import boto3
# os.chdir(config.project_working_directory)
cwd = os.getcwd()

client_data_path = config.client_data_path

twilio_phone = config.twilio_phone

aws_access_key_id= config.aws_access_key_id
aws_secret_access_key= config.aws_secret_access_key

client = twilioClient(config.twilio_account_sid, config.twilio_auth_token)

now=datetime.today()
date_str = now.strftime("%m/%d/%y")

morning_q_variations = [
    'what good will you do on this day?',
    'what good will you do today?',
    'how will you make progress today?',
    'how will you progress towards your goals today?'
    ]
evening_q_variations = [
    'what good did you do on this day?',
    'what good did you do today?',
    'how did you make progress today?',
    'how did you progress towards your goals today?'
    ]
celebration_emojis = [
    '\U0001F605',
    '\U0001F642',
    '\U0001F604',
    '\U0001F60A',
    '\U0001F607',
    '\U0001F911',
    '\U0001F917',
    '\U0001F44F'
]
neutral_emojis = [
    '\U0001F44F',
    '\U0001F31F',
    '\U0001F381',
    '\U0001F300',
    '\U0001F308',
    '\U0001F30A',
    '\U0001F525',
    '','',''
]

def get_provided_prompt():
    key = config.aws_root_folder + '/' + 'prompts.csv'
    
    s3_client = boto3.client('s3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        )

    # s3 = session.resource('s3')
    obj = s3_client.get_object(
    Bucket = config.aws_bucket,
    Key = key
    )
    # Read data from the S3 object.
    prompts = pd.read_csv(io.BytesIO(obj['Body'].read()))
    
    #get current date to choose the prompt based off of.
    utc = pytz.timezone('UTC')
    now=utc.localize(datetime.today())
    date_str = now.strftime("%m/%d/%Y")
    msg = client.messages.create(
                    body= (date_str),
                    from_=twilio_phone,
                    to='+12058079007'
                )
    
    row = prompts[prompts['date']==date_str].reset_index()
    
    return row['prompt'][0]

def initiate_confirmation(nickname, phone):
    msg = client.messages.create(body = (
            "Hi " + nickname + ". This is your confirmation that Benji Text Message Journal has correctly received your phone number." + '\n' \
            + "Finish the checkout process to fully register!"
        ),
        from_=twilio_phone,
        to=str(int(phone))
    )

def welcome(nickname, to_number, doc_link):
    msg = client.messages.create(body = (
            "Hi " + nickname + ", welcome to Journal Jar." + '\n' + "I will help you plan your day and reflect at night." + '\n' + \
            "Simply respond each day to the morning and evening question that you will receive."
        ),
        from_=twilio_phone,
        to=str(int(to_number))
    )
    msg = client.messages.create(body = (
            "Your journal entries will be saved discreetly and can be accessed at this link: " \
            + '\n' + doc_link + '\n' + 'Send -help for additional info' + '\n' + 'Send -link anytime for your journal link'
        ),
        from_=twilio_phone,
        to=str(int(to_number))
    )


def morning(row):
    #default prompt(s)
    if pd.isna(row['mq_prompt']):
        try:
            msg = client.messages.create(
                body= row['nickname'] + ', ' + random.choice(morning_q_variations) + ' ' + random.choice(neutral_emojis),
                from_=twilio_phone,
                to=str(int(row['phone']))
                )
        except:
            print("Failed to send to " + str(row['phone']))
    #custom prompt
    else:
        try:
            msg = client.messages.create(
                body=row['mq_prompt'],
                from_=twilio_phone,
                to=str(int(row['phone']))
                )
        except:
            print("Failed to send to " + str(row['phone']))

def evening(row):
    #default prompt(s)
    if pd.isna(row['eq_prompt']):
        try:
            msg = client.messages.create(
                body= row['nickname'] + ', ' + random.choice(evening_q_variations) + ' ' + random.choice(celebration_emojis),
                from_=twilio_phone,
                to=str(int(row['phone']))
            )
        except:
            print("Failed to send to " + str(row['phone']))
    #custom prompt
    else:
        try:
            msg = client.messages.create(
                body= row['eq_prompt'],
                from_=twilio_phone,
                to=str(int(row['phone']))
                )
        except:
            print("Failed to send to " + str(row['phone']))

def score(phone):
    #move these to before score function is called in order to avoid circular import
    # update_journal_metadata('morning', phone)
    # update_journal_metadata('evening', phone)

    client_data = get_client_data()
    row = client_data[client_data['phone']==phone].reset_index()

    score_msg = (
            'Week morning entries: ' + str(int(row['morning_entry_qty_week'][0])) + '\n'
            'Week evening entries: ' + str(int(row['evening_entry_qty_week'][0])) + '\n'
            'Month morning entries: ' + str(int(row['morning_entry_qty_month'][0])) + '\n'
            'Month evening entries: ' + str(int(row['evening_entry_qty_month'][0])) + '\n'
            'To-date morning entries: ' + str(int(row['morning_entry_qty'][0])) + '\n'
            'To-date evening entries: ' + str(int(row['evening_entry_qty'][0])) + '\n'
            'Morning entry streak: ' + str(int(row['morning_entry_streak'][0])) + '\n'
            'Evening entry streak: ' + str(int(row['evening_entry_streak'][0])) + '\n'
        )
    return score_msg

def weekly_summary():
    #update journal metadata
    # update_all_client_metadata()
    #load clients with cst time zone and normal time wanted
    client_data = get_client_data()

    for id, row in client_data.iterrows():
        try:
            msg = client.messages.create(
                body= (
                    'Hi ' + row['nickname'] + ', here is your Benji weekly summary:' + '\n'
                    'You planned ' + str(int(row['morning_entry_qty_week'])) + ' times' + '\n'
                    'You reflected ' + str(int(row['evening_entry_qty_week'])) + ' times' + '\n'
                    "Send -score for additional stats"
                ),
                from_=twilio_phone,
                to=str(int(row['phone']))
            )
        except:
            print("Failed to send to " + str(row['phone']))
def test():
    msg = client.messages.create(
        body= "Scheduled Test " + random.choice(evening_q_variations),
        from_=twilio_phone,
        to='2058079007'
    )