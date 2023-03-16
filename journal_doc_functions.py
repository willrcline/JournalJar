import pandas as pd
import numpy as npA
from datetime import datetime, timedelta, date
import os
import time
import config
import pytz
# import s3fs
import boto3
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from client_data_functions import *
from msg_functions import get_provided_prompt
# os.chdir(config.project_working_directory)
cwd = os.getcwd()
client_data_path = config.client_data_path
journal_dir_path = config.aws_root_folder + '/' + config.journal_folder

aws_access_key_id= config.aws_access_key_id
aws_secret_access_key= config.aws_secret_access_key

twilio_phone = config.twilio_phone
client = Client(config.twilio_account_sid, config.twilio_auth_token)


#import users's journal, append new messages to journal doc, export to update
def append(phone, message_body, time):

    client_data = get_client_data()
    row = client_data[client_data['phone']==phone].reset_index()
    nickname = row['nickname'][0]
    file_name = nickname + "\'s" + " Benji Journal " + str(phone)
    file_path = journal_dir_path + '/' + file_name + '.txt'
    aws_key = config.aws_root_folder + '/' + config.journal_folder + '/' + file_name


#!!!create Entry header!!!
    # get current time in their time zone (defaults to central)
    if pd.isna(row['time_zone'][0]):
            now = datetime.now(pytz.timezone('America/Chicago'))
    else:
        now = datetime.now(pytz.timezone(row['time_zone'][0]))
    date_str = now.strftime("%m/%d/%y")
    day_of_week = now.strftime('%a')

    if (time == 'Morning') & (pd.notna(row['mq_prompt'][0])):
        prompt = row['mq_prompt'][0]
    elif (time == 'Evening') & (pd.notna(row['eq_prompt'][0])):
        prompt = row['eq_prompt'][0]
    else:
        prompt = get_provided_prompt()
    append_hdr = '--' + time + "-" + day_of_week + '-' + date_str + '--'
    append_ftr = '_______________________________________'
    if prompt == '':
        append_str = append_hdr + '\n' + message_body + '\n' + append_ftr + '\n\n'
    else:
        append_str = append_hdr + '\n' + prompt + '\n' + message_body + '\n' + append_ftr + '\n\n'
#!!!END OF create Entry header!!!

#!!!Read and write to file!!!
    object = read_s3_text_file(aws_key)
    lines = get_lines_from_s3_text_file_object(object)

    if append_hdr in lines:
        print('Not the first entry with this header')
        #find line index in list for next footer and insert message body right above it to be below all other entries
        ftr_index = lines.index(append_ftr)
        lines.insert(ftr_index, message_body)

        rejoined = '\n'.join(lines)
        result = object.put(Body=rejoined)

        # f.close()
        #reopen file in write mode to over write all
        # f = open(file_path, 'w')

        # for line in lines: # write lines list content
        #     f.write(line)
        # f.close()

        return('n')
    else:
        print("First entry of this sort")
        lines.insert(0, append_str)
        rejoined = '\n'.join(lines)
        result = object.put(Body=rejoined)

        return('y')
#!!!END OF Read and write to file!!!

def get_current_negative_streak(entry_dates):
    now=datetime.today()
    date_str = now.strftime("%m/%d/%y")
    yesterday_date_str = (now - timedelta(days=1)).strftime("%m/%d/%y")

    #no entries at all
    if len(entry_dates) == 0:
        return 0


    most_recent_date_str = entry_dates[0]
    most_recent_date = datetime.strptime(most_recent_date_str, "%m/%d/%y")

    num_days = date_str - most_recent_date
   
    return num_days

def get_current_streak(entry_dates):
    now=datetime.today()
    date_str = now.strftime("%m/%d/%y")
    yesterday_date_str = (now - timedelta(days=1)).strftime("%m/%d/%y")

    #no entries at all
    if len(entry_dates) == 0:
        return 0

    most_recent_date_str = entry_dates[0]
    most_recent_date = datetime.strptime(most_recent_date_str, "%m/%d/%y")
    #no entry for yesterday or today
    if (most_recent_date_str != date_str) and (most_recent_date_str != yesterday_date_str):
        return 0
    #most recent entry is from today or yesterday
    else:
        tally = 1
        more_recent_date = most_recent_date
        for date in entry_dates[1:]:
            if datetime.strptime(date, "%m/%d/%y") == more_recent_date - timedelta(days=1):
                #add a tally
                tally +=1
                #make more recent date become the date that you just iterated over
                more_recent_date = datetime.strptime(date, "%m/%d/%y")
        return tally

def get_usage_in_period(entry_dates, period):
    now=datetime.today()
    date_str = now.strftime("%m/%d/%y")

    #get all dates within time period compare to
    if period == 'week':
        x=7
        d = now.toordinal()
        last = d - 6
        su = last - (last % 7)
        sunday = date.fromordinal(su)
        dates = [(sunday + timedelta(days=idx)).strftime("%m/%d/%y") for idx in range(7)]
    elif period == 'month':
        x = 31
        month_start =  datetime.strptime((date_str.split('/')[0] + '/' + '01' + '/' + date_str.split('/')[2]), "%m/%d/%y")
        dates = [(month_start + timedelta(days=idx)).strftime("%m/%d/%y") for idx in range(31)]

    tally = 0
    for entry_date in entry_dates[:x]:
        if entry_date in dates:
            tally += 1
    return tally


#returns object of s3 text file
def read_s3_text_file(aws_key):
    boto3_session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
    s3 = boto3_session.resource('s3')
    object = s3.Object(config.aws_bucket, aws_key)
    
    return object

def get_lines_from_s3_text_file_object(object):
    current_text = str(object.get()['Body'].read().decode(encoding="utf-8",errors="ignore"))
    lines = current_text.splitlines()
    return lines
  
def get_entry_dates(m_or_e, phone):
    m_or_e = m_or_e.capitalize()
    #import client data
    client_data = get_client_data()
    row = client_data[client_data['phone']==phone].reset_index()
    nickname = row['nickname'][0]

    #locate client journal doc
    file_name = nickname + "\'s" + " Journal " + str(phone)
    file_path = journal_dir_path + '/' + file_name + '.txt'
    aws_key = config.aws_root_folder + '/' + config.journal_folder + '/' + file_name
    
    lines = read_s3_text_file(aws_key)

    entry_hdr_tag = '--' + m_or_e + "-"
    #gather metadata about journal doc
    tally = 0
    entry_dates = []
    for line in lines:
        if entry_hdr_tag in line:
            entry_date = line.split("-")[3]
            entry_dates.append(entry_date)
            tally += 1
            
    return entry_dates

def update_journal_metadata(phone):
    client_data = get_client_data()
    row = client_data[client_data['phone']==phone].reset_index()
    tally = 0

    morning_entry_dates = get_entry_dates("morning", phone)
    evening_entry_dates = get_entry_dates("evening", phone)

    #put metadata in client datatable
    #call function to return streak data
    streak = get_current_streak(morning_entry_dates)
    client_data.loc[client_data.phone==phone,'morning_entry_streak']=streak
  
    #call function to return negative streak data
    negative_streak = get_current_negative_streak(morning_entry_dates)
    client_data.loc[client_data.phone==phone,'morning_entry_negative_streak']=negative_streak
   
    #compares all negative streaks to get an absolute negative streak
    abs_negative_streak = min([row['morning_entry_negative_streak'][0],negative_streak])
    client_data.loc[client_data.phone==phone,'abs_negative_streak'] = abs_negative_streak
   
    #call function to return this month and week's usage
    week_usage = get_usage_in_period(morning_entry_dates, 'week')
    month_usage = get_usage_in_period(morning_entry_dates, 'month')
    client_data.loc[client_data.phone==phone,'morning_entry_qty_week']= week_usage
    client_data.loc[client_data.phone==phone,'morning_entry_qty_month']= month_usage

    client_data.loc[client_data.phone==phone,'morning_entry_qty']=tally
    #add most recent entry date if there is one
    if tally != 0:
        client_data.loc[client_data.phone==phone,'most_recent_morning_entry_date']=morning_entry_dates[0]
    else:
        client_data.loc[client_data.phone==phone,'most_recent_morning_entry_date']=np.nan

    #evening
    #call function to return streak data
    streak = get_current_streak(evening_entry_dates)
    client_data.loc[client_data.phone==phone,'evening_entry_streak']=streak

    #call function to return negative streak data
    negative_streak = get_current_negative_streak(evening_entry_dates)
    client_data.loc[client_data.phone==phone,'evening_entry_negative_streak']=negative_streak
    #compares all negative streaks to get an absolute negative streak
    abs_negative_streak = min([row['morning_entry_negative_streak'][0],negative_streak])
    client_data.loc[client_data.phone==phone,'abs_negative_streak'] = abs_negative_streak

    #call function to return this month and week's usage
    week_usage = get_usage_in_period(evening_entry_dates, 'week')
    month_usage = get_usage_in_period(evening_entry_dates, 'month')
    client_data.loc[client_data.phone==phone,'evening_entry_qty_week']= week_usage
    client_data.loc[client_data.phone==phone,'evening_entry_qty_month']= month_usage

    client_data.loc[client_data.phone==phone,'evening_entry_qty']=tally
    #add most recent entry date if there is one
    if tally != 0:
        client_data.loc[client_data.phone==phone,'most_recent_evening_entry_date']=evening_entry_dates[0]
    else:
        client_data.loc[client_data.phone==phone,'most_recent_evening_entry_date']=np.nan
    #overwrite csv
    put_client_data(client_data)


def update_all_client_metadata():
    client_data = get_client_data()

    for phone in client_data['phone']:
        try:
            update_journal_metadata(phone)
        except:
            print('evening', phone)