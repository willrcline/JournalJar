from client_data_functions import get_client_data, put_client_data
from flask import request, session, render_template
from flask import Blueprint
import pandas as pd


app_blueprint = Blueprint('app_blueprint', __name__)

@app_blueprint.route('/portal')
def portal():
    # save changes button is pressed:
    if request.method == 'POST':
        #read in client data
        client_data = get_client_data()
        row = client_data[client_data['email']==session['user']['email']].reset_index()


        #-----START of update database with user inputs to settings menu--------------------

        try:
            account_active_input = request.form["account_active"]
            account_active_input = "y"
        except:
            account_active_input = "n"
        client_data.loc[client_data.email == row['email'][0] ,'account_active']=account_active_input

        try:
            mq_toggle_flag_input = request.form["mq_toggle_flag"]
            mq_toggle_flag_input = "y"
        except:
            mq_toggle_flag_input = "n"
        client_data.loc[client_data.email == row['email'][0] ,'mq_toggle_flag']=mq_toggle_flag_input
        try:
            eq_toggle_flag_input = request.form["eq_toggle_flag"]
            eq_toggle_flag_input = "y"
        except:
            eq_toggle_flag_input = "n"
        client_data.loc[client_data.email == row['email'][0] ,'eq_toggle_flag']=eq_toggle_flag_input
        try:
            wq_toggle_flag_input = request.form["wq_toggle_flag"]
            wq_toggle_flag_input = "y"
        except:
            wq_toggle_flag_input = "n"
        client_data.loc[client_data.email == row['email'][0] ,'wq_toggle_flag']=wq_toggle_flag_input

        try:
            time_zone_input = request.form["time_zone"]
            client_data.loc[client_data.email == row['email'][0] ,'time_zone']=time_zone_input
        except:
            pass

        try:
            mq_time_input = request.form["mq_time"]
            client_data.loc[client_data.email == row['email'][0] ,'mq_time']=mq_time_input
        except:
            pass
        try:
            eq_time_input = request.form["eq_time"]
            client_data.loc[client_data.email == row['email'][0] ,'eq_time']=eq_time_input
        except:
            pass
        try:
            wq_time_input = request.form["wq_time"]
            client_data.loc[client_data.email == row['email'][0] ,'wq_time']=wq_time_input
        except:
            pass



        mq_prompt_input = request.form["mq_prompt"]
        if mq_prompt_input != "":
            client_data.loc[client_data.email == row['email'][0] ,'mq_prompt']=mq_prompt_input
        eq_prompt_input = request.form["eq_prompt"]
        if eq_prompt_input != "":
            client_data.loc[client_data.email == row['email'][0] ,'eq_prompt']=eq_prompt_input
        # wq_prompt_input = request.form["wq_prompt"]
        # if wq_prompt_input != "":
        #     client_data.loc[client_data.email == row['email'][0] ,'wq_prompt']=wq_prompt_input

        #export data updates
        put_client_data(client_data)

        #-----END of update database with user inputs to settings menu-----------------------

        #-------START of exact copy of the code for GET request to /portal--------
        client_data = get_client_data()
        row = client_data[client_data['email']==session['user']['email']].reset_index()

        #Get user stats
        if pd.isna(row['morning_entry_qty_month'][0]):
            morning_entry_qty_month = 0
        else:
            morning_entry_qty_month = row['morning_entry_qty_month'][0]
        if pd.isna(row['evening_entry_qty_month'][0]):
            evening_entry_qty_month = 0
        else:
            evening_entry_qty_month = row['evening_entry_qty_month'][0]
        # Get streak data and streak_msg to display on portal
        abs_positive_streak = row['abs_positive_streak'][0]
        abs_negative_streak = row['abs_negative_streak'][0]
        if (abs_negative_streak == 0) & (abs_positive_streak == 0):
            streak_msg = "Streak: " + str(int(abs_positive_streak))
        elif abs_positive_streak > 0:
            streak_msg = "Streak: " + str(int(abs_positive_streak))
        elif abs_negative_streak > 0:
            #days until penalty only potentially accurate if first penatly charge in abs_negative_streak
            streak_msg = "Negative Streak: " + str(int(abs_negative_streak)) + ". Days until penalty: " + str(int(7 - abs_negative_streak)) 

        #Get current user settings
        if pd.isna(row['time_zone'][0]):
            time_zone = "US/Central"
        else:
            time_zone = row["time_zone"][0]
        if pd.isna(row['mq_time'][0]):
            mq_time = "07:30"
        else:
            mq_time = row["mq_time"][0]
        if pd.isna(row['eq_time'][0]):
            eq_time = "20:30"
        else:
            eq_time = row["eq_time"][0]
        if pd.isna(row['wq_time'][0]):
            wq_time = "18:30"
        else:
            wq_time = row["wq_time"][0]
        if pd.isna(row['mq_prompt'][0]):
            mq_prompt = "ie. What good will you do today?"
        else:
            mq_prompt = row["mq_prompt"][0]
        if pd.isna(row['eq_prompt'][0]):
            eq_prompt = "ie. What good did you do today?"
        else:
            eq_prompt = row["eq_prompt"][0]
        if pd.isna(row['wq_prompt'][0]):
            wq_prompt = "ie. What good did you do this week?"
        else:
            wq_prompt = row["wq_prompt"][0]
        if row['account_active'][0].lower() == 'y':
            account_active_toggle = 'checked'
        else:
            account_active_toggle = ''

        if ( (pd.isna(row['mq_toggle_flag'][0])) or (row['mq_toggle_flag'][0]=='y') ):
            mq_toggle = 'checked'
        else:
            mq_toggle = ''
        if ( (pd.isna(row['eq_toggle_flag'][0])) or (row['eq_toggle_flag'][0]=='y') ):
            eq_toggle = 'checked'
        else:
            eq_toggle = ''
        if ( (pd.isna(row['wq_toggle_flag'][0])) or (row['wq_toggle_flag'][0]=='y') ):
            wq_toggle = 'checked'
        else:
            wq_toggle = ''

        return render_template('existing_user.html',
        row=row, doc_link= row['doc_link'][0],
        #user stats
        morning_entry_qty_month= morning_entry_qty_month, 
        evening_entry_qty_month=evening_entry_qty_month,
        streak_msg=streak_msg,
        #current user settings
        mq_time=mq_time,
        eq_time=eq_time,
        wq_time=wq_time,
        mq_prompt=mq_prompt,
        eq_prompt=eq_prompt,
        wq_prompt=wq_prompt,
        time_zone=time_zone,
        account_active_toggle=account_active_toggle,
        mq_toggle=mq_toggle,
        eq_toggle=eq_toggle,
        wq_toggle=wq_toggle
        )

        #-------END of exact copy of the code for GET request to /portal--------    #GET request to /portal:
    else:
        client_data = get_client_data()
        row = client_data[client_data['email']==session['user']['email']].reset_index()

        #Get user stats
        if pd.isna(row['morning_entry_qty_month'][0]):
            morning_entry_qty_month = 0
        else:
            morning_entry_qty_month = row['morning_entry_qty_month'][0]
        if pd.isna(row['evening_entry_qty_month'][0]):
            evening_entry_qty_month = 0
        else:
            evening_entry_qty_month = row['evening_entry_qty_month'][0]
        # Get streak data and streak_msg to display on portal
        abs_positive_streak = row['abs_positive_streak'][0]
        abs_negative_streak = row['abs_negative_streak'][0]
        if (abs_negative_streak == 0) & (abs_positive_streak == 0):
            streak_msg = "Streak: " + str(int(abs_positive_streak))
        elif abs_positive_streak > 0:
            streak_msg = "Streak: " + str(int(abs_positive_streak))
        elif abs_negative_streak > 0:
            #days until penalty only potentially accurate if first penatly charge in abs_negative_streak
            streak_msg = "Negative Streak: " + str(int(abs_negative_streak)) + ". Days until penalty: " + str(int(7 - abs_negative_streak)) 
        
        #error in abs neg or pos streak data
        else:
            streak_msg = "?"

        #Get current user settings
        if pd.isna(row['time_zone'][0]):
            time_zone = "US/Central"
        else:
            time_zone = row["time_zone"][0]
        if pd.isna(row['mq_time'][0]):
            mq_time = "07:30"
        else:
            mq_time = row["mq_time"][0]
        if pd.isna(row['eq_time'][0]):
            eq_time = "20:30"
        else:
            eq_time = row["eq_time"][0]
        if pd.isna(row['wq_time'][0]):
            wq_time = "18:30"
        else:
            wq_time = row["wq_time"][0]
        if pd.isna(row['mq_prompt'][0]):
            mq_prompt = "ie. What good will you do today?"
        else:
            mq_prompt = row["mq_prompt"][0]
        if pd.isna(row['eq_prompt'][0]):
            eq_prompt = "ie. What good did you do today?"
        else:
            eq_prompt = row["eq_prompt"][0]
        if pd.isna(row['wq_prompt'][0]):
            wq_prompt = "ie. What good did you do this week?"
        else:
            wq_prompt = row["wq_prompt"][0]
        if row['account_active'][0].lower() == 'y':
            account_active_toggle = 'checked'
        else:
            account_active_toggle = ''

        if ( (pd.isna(row['mq_toggle_flag'][0])) or (row['mq_toggle_flag'][0]=='y') ):
            mq_toggle = 'checked'
        else:
            mq_toggle = ''
        if ( (pd.isna(row['eq_toggle_flag'][0])) or (row['eq_toggle_flag'][0]=='y') ):
            eq_toggle = 'checked'
        else:
            eq_toggle = ''
        if ( (pd.isna(row['wq_toggle_flag'][0])) or (row['wq_toggle_flag'][0]=='y') ):
            wq_toggle = 'checked'
        else:
            wq_toggle = ''

        return render_template('existing_user.html',
            row=row, doc_link= row['doc_link'][0],
            #user stats
            morning_entry_qty_month= morning_entry_qty_month, 
            evening_entry_qty_month=evening_entry_qty_month,
            streak_msg=streak_msg,
            #current user settings
            mq_time=mq_time,
            eq_time=eq_time,
            wq_time=wq_time,
            mq_prompt=mq_prompt,
            eq_prompt=eq_prompt,
            wq_prompt=wq_prompt,
            time_zone=time_zone,
            account_active_toggle=account_active_toggle,
            mq_toggle=mq_toggle,
            eq_toggle=eq_toggle,
            wq_toggle=wq_toggle
        )
