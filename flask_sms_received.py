import config
from journal_doc_functions import append, update_journal_metadata
from time_functions import to_utc
from msg_functions import get_provided_prompt
from drive_functions import updateFile
from client_data_functions import get_client_data, put_client_data
# from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import pandas as pd
from datetime import datetime
import random

twilio_phone = config.twilio_phone
twilio_client = Client(config.twilio_account_sid, config.twilio_auth_token)


def sms_received():
    if request.method == 'POST':
        #get their msg info
        phone = int(request.form['From'][2:])
        message_body = request.form['Body']

        #get their data table info
        client_data = get_client_data()
        row = client_data[client_data['phone']==phone].reset_index()

        if row['account_active'][0] == 'y':
            doc_link = row['doc_link'][0]
            nickname = row['nickname'][0]
            file_id = row['file_id'][0]

            wants_responses_flag = row['wants_responses_flag'][0]

            today = datetime.today()

           #default to 7:30 for morning question time
            if pd.isna(row['mq_time'][0]):
                mq_time = "07:30"
            else:
                mq_time = row['mq_time'][0]
            #default to 8:30 PM for evening question time
            if pd.isna(row['eq_time'][0]):
                eq_time = "20:30"
            else:
                eq_time = row['eq_time'][0]
            if pd.isna(row['time_zone'][0]):
                time_zone = "US/Central"
            else:
                time_zone = row['time_zone'][0]

            mq_dt = to_utc(mq_time, time_zone)
            eq_dt = to_utc(eq_time, time_zone)

            #get current datetime to decide what to do with their message
            utc_now = pytz.timezone('UTC').localize(datetime.utcnow())

            #create response object
            resp = MessagingResponse()

            if (message_body == '-client data') & (phone == 2058079007):
                backup_client_data()
                client_data_link = r"https://drive.google.com/file/d/1PntgcNTL0oLH52HVqOnoOyrCPpYAtGbu/view?usp=sharing"
                msg = twilio_client.messages.create(
                    body= (client_data_link),
                    from_=config.twilio_phone,
                    to='+12058079007'
                )
            elif message_body == '-help':
                resp.message('You have requested help. Click this link to read technical support docs for Benji:' + '\n')
            elif message_body == '-support':
                resp.message('You have requested personal assistance for technical or billing support.' + '\n' + 'You will receive a text or call from a technician as soon as possible.' \
                    + '\n' + 'Your technician will reach you from this number: 2058079007.')
                msg = twilio_client.messages.create(
                    body= (str(phone) + ' has requested technical support from the Benji interface.'),
                    from_=config.twilio_phone,
                    to='+12058079007'
                )
            elif (message_body == '-link') or (message_body == '-journal'):
                resp.message(doc_link)
            #Morning question
            elif ( ( (pd.isna(row['mq_toggle_flag'][0])) or (row['mq_toggle_flag'][0]=='y') ) & (utc_now >= mq_dt ) and (utc_now <= mq_dt + timedelta(hours=5)) ):
                new_entry_flag = append(phone, message_body, 'Morning')
                updateFile(nickname, phone, file_id)
                if wants_responses_flag != 'n':
                    if new_entry_flag == 'y':
                        #update streak data then read back in row and find row based on phone number to get updated streak data.
                        update_journal_metadata(phone)
                        client_data = get_client_data()
                        row = client_data[client_data['phone']==row['phone']].reset_index()
                        #add one to streak to include today
                        morning_entry_streak = str(int(row['morning_entry_streak'][0]) + 1)

                        if random.random() < 0.2:
                            resp.message('New morning entry created. Remember you can send -link for journal link at anytime. Send -help for additional info.' + \
                            '\n' + "\U00002714Streak: " + morning_entry_streak)
                        else:
                            resp.message('New morning entry created'+ \
                            '\n' + "\U00002714Streak: " + morning_entry_streak)
                    else:
                        resp.message('Added')
            #Evening question
            elif( ( (pd.isna(row['eq_toggle_flag'][0])) or (row['eq_toggle_flag'][0]=='y') ) & (utc_now >= eq_dt) and (utc_now <= eq_dt + timedelta(hours=5)) ):
                new_entry_flag = append(phone, message_body, 'Evening')
                updateFile(nickname, phone, file_id)

                if wants_responses_flag != 'n':
                    if new_entry_flag == 'y':
                        #update streak data then read back in row and find row based on phone number to get updated streak data.
                        update_journal_metadata(phone)
                        client_data = get_client_data()
                        row = client_data[client_data['phone']==row['phone']].reset_index()
                        #add one to streak to include today
                        evening_entry_streak = str(int(row['evening_entry_streak'][0]) + 1)
                        if random.random() < 0.2:
                            resp.message('New evening entry created. Remember you can send -link for journal link at anytime. Send -help for additional info.' + \
                            '\n' + "\U00002714Streak: " + evening_entry_streak)
                        else:
                            resp.message('New evening entry created' + \
                            '\n' + "\U00002714Streak: " + evening_entry_streak)
                    else:
                        resp.message('Added')
            return str(resp)
    if request.method == 'GET':       
        return "<p> Get SMS </p>"