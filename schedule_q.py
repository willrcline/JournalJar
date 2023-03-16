# # from twilio.twiml.messaging_response import MessagingResponse
# # from twilio.rest import Client
# # import pandas as pd
# # #twilio
# # twilio_account_sid = 'AC68279e2192dfd6cc97636821ca37906b'
# # twilio_auth_token = 'ed5dbd4e74d9c3806a1d451525e80573'
# # twilio_phone = '+16292496969'
# # client = Client(twilio_account_sid, twilio_auth_token)

# # msg = client.messages.create(
# #                     body= "test_send.py executed",
# #                     from_=twilio_phone,
# #                     to='+12058079007'
# #                 )


                
# #!!!this file needs to be scheduled to run every 30 minutes to initiate outgoing messages!!!

# #Possible pip dependencies:
# # pytz==2022.6
# # python-dateutil==2.8.2
# # twilio==7.15.4
# # pandas==1.5.2
# # boto3==1.26.24
# # botocore==1.29.24

# import time
# from datetime import datetime
# import pandas as pd
# from twilio.twiml.messaging_response import MessagingResponse
# from twilio.rest import Client
# import pytz
# import boto3
# import io
# import random

# #config information:
# # twilio
# twilio_account_sid = 'AC68279e2192dfd6cc97636821ca37906b'
# twilio_auth_token = 'ed5dbd4e74d9c3806a1d451525e80573'
# twilio_phone = '+16292496969'
# client = Client(twilio_account_sid, twilio_auth_token)
# # aws
# aws_access_key_id='AKIATVWG33Z6UKQSV2F7'
# aws_secret_access_key='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'
# #  s3 file paths
# aws_bucket_path = "s3://elasticbeanstalk-us-west-2-252746391165"
# aws_root_folder = 'ben-storage'
# aws_bucket = "elasticbeanstalk-us-west-2-252746391165"
# aws_key = aws_root_folder + '/' + 'client_data.csv'
# journal_folder = 'journals'
# client_data_path = aws_bucket_path + '/' + aws_root_folder + '/' + "client_data.csv"

# #Extra variables
# morning_q_variations = [
#     'what good will you do on this day?',
#     'what good will you do today?',
#     'how will you make progress today?',
#     'how will you progress towards your goals today?'
#     ]
# evening_q_variations = [
#     'what good did you do on this day?',
#     'what good did you do today?',
#     'how did you make progress today?',
#     'how did you progress towards your goals today?'
#     ]
# celebration_emojis = [
#     '\U0001F605',
#     '\U0001F642',
#     '\U0001F604',
#     '\U0001F60A',
#     '\U0001F607',
#     '\U0001F911',
#     '\U0001F917',
#     '\U0001F44F'
# ]
# neutral_emojis = [
#     '\U0001F44F',
#     '\U0001F31F',
#     '\U0001F381',
#     '\U0001F300',
#     '\U0001F308',
#     '\U0001F30A',
#     '\U0001F525',
#     '','',''
# ]

# #Functions
# # client_data_functions
# def get_client_data():
#     s3_client = boto3.client('s3',
#         aws_access_key_id=aws_access_key_id,
#         aws_secret_access_key=aws_secret_access_key,
#         )

#     # s3 = session.resource('s3')
#     obj = s3_client.get_object(
#     Bucket = aws_bucket,
#     Key = aws_key
#     )
#     # Read data from the S3 object.
#     client_data = pd.read_csv(io.BytesIO(obj['Body'].read()))
    
#     return client_data

# def put_client_data(client_data):
#     s3_client = boto3.client('s3',
#         aws_access_key_id=aws_access_key_id,
#         aws_secret_access_key=aws_secret_access_key,
#         )

#     csv_buf = io.StringIO()
#     client_data.to_csv(csv_buf, header=True, index=False)
#     csv_buf.seek(0)
#     s3_client.put_object(Bucket = aws_bucket,Key = aws_key, Body=csv_buf.getvalue())
    
# # time_functions
# def to_utc(time, time_zone):
#     utc = pytz.timezone('UTC')
#     now = utc.localize(datetime.utcnow())
#     #timezone of choice
#     tz = pytz.timezone(time_zone)

#     #create timestamp in timezone of choice
#     local_time = now.astimezone(tz)

#     #now that I have an object with the right properties, replace the hour and minute to what you need it to be
#     h = int(time.split(":")[0])
#     m = int(time.split(":")[1])
#     local_time = local_time.replace(hour=h)
#     local_time = local_time.replace(minute=m)

#     local_time = local_time.astimezone(utc)
#     return local_time

# # msg_functions
# def morning(row):
#     #default prompt(s)
#     if pd.isna(row['mq_prompt']):
#         try:
#             msg = client.messages.create(
#                 body= row['nickname'] + ', ' + random.choice(morning_q_variations) + ' ' + random.choice(neutral_emojis),
#                 from_=twilio_phone,
#                 to=str(int(row['phone']))
#                 )
#         except:
#             print("Failed to send to " + str(row['phone']))
#     #custom prompt
#     else:
#         try:
#             msg = client.messages.create(
#                 body=row['mq_prompt'],
#                 from_=twilio_phone,
#                 to=str(int(row['phone']))
#                 )
#         except:
#             print("Failed to send to " + str(row['phone']))

# def evening(row):
#     #default prompt(s)
#     if pd.isna(row['eq_prompt']):
#         try:
#             msg = client.messages.create(
#                 body= row['nickname'] + ', ' + random.choice(evening_q_variations) + ' ' + random.choice(celebration_emojis),
#                 from_=twilio_phone,
#                 to=str(int(row['phone']))
#             )
#         except:
#             print("Failed to send to " + str(row['phone']))
#     #custom prompt
#     else:
#         try:
#             msg = client.messages.create(
#                 body= row['eq_prompt'],
#                 from_=twilio_phone,
#                 to=str(int(row['phone']))
#                 )
#         except:
#             print("Failed to send to " + str(row['phone']))

# # journal_doc_functions
# def get_current_negative_streak(entry_dates):
#     now=datetime.today()
#     date_str = now.strftime("%m/%d/%y")
#     yesterday_date_str = (now - timedelta(days=1)).strftime("%m/%d/%y")

#     #no entries at all
#     if len(entry_dates) == 0:
#         return 0

#     most_recent_date_str = entry_dates[0]
#     most_recent_date = datetime.strptime(most_recent_date_str, "%m/%d/%y")

#     num_days = date_str - most_recent_date
   
#     return num_days

# def get_current_streak(entry_dates):
#     now=datetime.today()
#     date_str = now.strftime("%m/%d/%y")
#     yesterday_date_str = (now - timedelta(days=1)).strftime("%m/%d/%y")

#     #no entries at all
#     if len(entry_dates) == 0:
#         return 0

#     most_recent_date_str = entry_dates[0]
#     most_recent_date = datetime.strptime(most_recent_date_str, "%m/%d/%y")
#     #no entry for yesterday or today
#     if (most_recent_date_str != date_str) and (most_recent_date_str != yesterday_date_str):
#         return 0
#     #most recent entry is from today or yesterday
#     else:
#         tally = 1
#         more_recent_date = most_recent_date
#         for date in entry_dates[1:]:
#             if datetime.strptime(date, "%m/%d/%y") == more_recent_date - timedelta(days=1):
#                 #add a tally
#                 tally +=1
#                 #make more recent date become the date that you just iterated over
#                 more_recent_date = datetime.strptime(date, "%m/%d/%y")
#         return tally

# def get_usage_in_period(entry_dates, period):
#     now=datetime.today()
#     date_str = now.strftime("%m/%d/%y")

#     #get all dates within time period compare to
#     if period == 'week':
#         x=7
#         d = now.toordinal()
#         last = d - 6
#         su = last - (last % 7)
#         sunday = date.fromordinal(su)
#         dates = [(sunday + timedelta(days=idx)).strftime("%m/%d/%y") for idx in range(7)]
#     elif period == 'month':
#         x = 31
#         month_start =  datetime.strptime((date_str.split('/')[0] + '/' + '01' + '/' + date_str.split('/')[2]), "%m/%d/%y")
#         dates = [(month_start + timedelta(days=idx)).strftime("%m/%d/%y") for idx in range(31)]

#     tally = 0
#     for entry_date in entry_dates[:x]:
#         if entry_date in dates:
#             tally += 1
#     return tally
    
# def read_s3_text_file(aws_key):
#     boto3_session = boto3.Session(
#                 aws_access_key_id=aws_access_key_id,
#                 aws_secret_access_key=aws_secret_access_key
#             )
#     s3 = boto3_session.resource('s3')
#     object = s3.Object(config.aws_bucket, aws_key)
#     current_text = str(object.get()['Body'].read().decode(encoding="utf-8",errors="ignore"))
#     lines = current_text.splitlines()
    
#     return lines
    
# def get_entry_dates(m_or_e, phone):
#     m_or_e = m_or_e.capitalize()
#     #import client data
#     client_data = get_client_data()
#     row = client_data[client_data['phone']==phone].reset_index()
#     nickname = row['nickname'][0]

#     #locate client journal doc
#     file_name = nickname + "\'s" + " Benji Journal " + str(phone)
#     file_path = journal_dir_path + '/' + file_name + '.txt'
#     aws_key = config.aws_root_folder + '/' + config.journal_folder + '/' + file_name
    
#     lines = read_s3_text_file(aws_key)

#     entry_hdr_tag = '%%-' + m_or_e + "-"
#     #gather metadata about journal doc
#     tally = 0
#     entry_dates = []
#     for line in lines:
#         if entry_hdr_tag in line:
#             entry_date = line.split("-")[3]
#             entry_dates.append(entry_date)
#             tally += 1
            
#     return entry_dates

# def update_journal_metadata(phone):
#     morning_entry_dates = get_entry_dates("morning", phone)
#     evening_entry_dates = get_entry_dates("evening", phone)
    
#     msg = client.messages.create(
#         body= "morning entry dates: "+ str(morning_entry_dates),
#         from_=twilio_phone,
#         to='2058079007'
#     )
#     # msg = client.messages.create(
#     #     body= "evening entry dates: "+ str(evening_entry_dates),
#     #     from_=twilio_phone,
#     #     to='2058079007'
#     # )

#     #put metadata in client datatable
#     #call function to return streak data
#     streak = get_current_streak(morning_entry_dates)
#     client_data.loc[client_data.phone==phone,'morning_entry_streak']=streak
#     msg = client.messages.create(
#         body= "morning streak: "+ str(streak),
#         from_=twilio_phone,
#         to='2058079007'
#     )

#     #call function to return negative streak data
#     negative_streak = get_current_negative_streak(morning_entry_dates)
#     client_data.loc[client_data.phone==phone,'morning_entry_negative_streak']=negative_streak
#     msg = client.messages.create(
#         body= "negative streak: "+ str(negative_streak),
#         from_=twilio_phone,
#         to='2058079007'
#     )
#     #compares all negative streaks to get an absolute negative streak
#     abs_negative_streak = min([row['morning_entry_negative_streak'][0],negative_streak])
#     client_data.loc[client_data.phone==phone,'abs_negative_streak'] = abs_negative_streak
#     msg = client.messages.create(
#         body= "abs negative streak: "+ str(abs_negative_streak),
#         from_=twilio_phone,
#         to='2058079007'
#     )
    
#     #call function to return this month and week's usage
#     week_usage = get_usage_in_period(morning_entry_dates, 'week')
#     month_usage = get_usage_in_period(morning_entry_dates, 'month')
#     client_data.loc[client_data.phone==phone,'morning_entry_qty_week']= week_usage
#     client_data.loc[client_data.phone==phone,'morning_entry_qty_month']= month_usage

#     client_data.loc[client_data.phone==phone,'morning_entry_qty']=tally
#     #add most recent entry date if there is one
#     if tally != 0:
#         client_data.loc[client_data.phone==phone,'most_recent_morning_entry_date']=morning_entry_dates[0]
#     else:
#         client_data.loc[client_data.phone==phone,'most_recent_morning_entry_date']=np.nan

#     #evening
#     #call function to return streak data
#     streak = get_current_streak(evening_entry_dates)
#     client_data.loc[client_data.phone==phone,'evening_entry_streak']=streak

#     #call function to return negative streak data
#     negative_streak = get_current_negative_streak(evening_entry_dates)
#     client_data.loc[client_data.phone==phone,'evening_entry_negative_streak']=negative_streak
#     #compares all negative streaks to get an absolute negative streak
#     abs_negative_streak = min([row['morning_entry_negative_streak'][0],negative_streak])
#     client_data.loc[client_data.phone==phone,'abs_negative_streak'] = abs_negative_streak

#     #call function to return this month and week's usage
#     week_usage = get_usage_in_period(evening_entry_dates, 'week')
#     month_usage = get_usage_in_period(evening_entry_dates, 'month')
#     client_data.loc[client_data.phone==phone,'evening_entry_qty_week']= week_usage
#     client_data.loc[client_data.phone==phone,'evening_entry_qty_month']= month_usage

#     client_data.loc[client_data.phone==phone,'evening_entry_qty']=tally
#     #add most recent entry date if there is one
#     if tally != 0:
#         client_data.loc[client_data.phone==phone,'most_recent_evening_entry_date']=evening_entry_dates[0]
#     else:
#         client_data.loc[client_data.phone==phone,'most_recent_evening_entry_date']=np.nan
#     #overwrite csv
#     put_client_data(client_data)

# def update_all_client_metadata():
#     client_data = get_client_data()

#     for phone in client_data['phone']:
#         try:
#             update_journal_metadata(phone)
#         except:
#             print('error in updating journal metadata for ', str(phone))
#             msg = client.messages.create(
#                 body= 'error in updating journal metadata for '+ str(phone),
#                 from_=twilio_phone,
#                 to='2058079007'
#             )
            
    
# #schedule_q
# client_data = get_client_data()
# utc_now = datetime.utcnow() #current utc time (operating system's time)

# for id, row in client_data.iterrows():
#     if row['account_active'] == 'y':
#         #Use user question times and time zone: convert to UTC

#         #defalut to central time zone
#         if pd.isna(row['time_zone']):
#             time_zone = "US/Central"
#         else:
#             time_zone = row['time_zone']

#         #default to 7:30 for morning question time
#         if pd.isna(row['mq_time']):
#             mq_time = "07:30"
#         else:
#             mq_time = row['mq_time']
#         #default to 8:30 PM for evening question time
#         if pd.isna(row['eq_time']):
#             eq_time = "20:30"
#         else:
#             eq_time = row['eq_time']

#         mq_dt = to_utc(mq_time, time_zone)
#         eq_dt = to_utc(eq_time, time_zone)
#         #get 9am in user's time_zone to update_journal_metadata() and trigger incentive at that time.
#         incentive_trigger_time = to_utc("09:00", time_zone)
        
        
#         #update_journal_metadata() at [9am] then check for sufficient negative streak
#         if ( (pd.isna(row['mq_toggle_flag'])) or (row['mq_toggle_flag']=='y') ) & (utc_now.hour == incentive_trigger_time.hour) & (utc_now.minute >= incentive_trigger_time.minute) & (utc_now.minute < incentive_trigger_time.minute + 10):
#             update_journal_metadata(row['phone'])
#             #read back in client data and find row based on phone number to get updated streak data. From this point on, row will need a "[0]" at the end of it.
#             client_data = get_client_data()
#             row = client_data[client_data['phone']==row['phone']].reset_index()
            
#         if (row['morning_entry_negative_streak'][0] == 7) or (row['evening_entry_negative_streak'][0] == 7):
#             msg = client.messages.create(
#                     body= row['email'][0] + " has had a significant negative streak.",
#                     from_=twilio_phone,
#                     to='+12058079007'
#                 )
#             msg = client.messages.create(
#                     body= "You have missed 7 days of journaling. You must pay the jar.",
#                     from_=twilio_phone,
#                     to=str(row['phone'][0])
#                 )
                
#         #morning() and evening() prompt sent if appropriate
#         if ( (pd.isna(row['mq_toggle_flag'][0])) or (row['mq_toggle_flag'][0]=='y') ) & (utc_now.hour == mq_dt.hour) & (utc_now.minute >= mq_dt.minute) & (utc_now.minute < mq_dt.minute + 10):
#             print('sending mq for ' + row['nickname'][0])
#             morning(row)
#         if ( (pd.isna(row['eq_toggle_flag'][0])) or (row['eq_toggle_flag'][0]=='y') ) & (utc_now.hour == eq_dt.hour) & (utc_now.minute >= eq_dt.minute) & (utc_now.minute < eq_dt.minute + 10):
#             print('sending eq for ' + row['nickname'][0])
#             evening(row)
            


# #Weekly summary
# # cst_now = datetime.now(pytz.timezone('America/Chicago'))
# # cst_day_of_week = cst_now.strftime('%a')
# # wkly_summary_time = datetime(2000, 1, 1, 0, 30, 0)
# # if (cst_day_of_week == 'Sun') & (utc_now.hour == wkly_summary_time.hour) & (utc_now.minute >= wkly_summary_time.minute) & (utc_now.minute < wkly_summary_time.minute + 5):
# #     weekly_summary()

