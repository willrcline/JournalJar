# File Structure


## Main files

### sms.py
This is the flask server always running.
It renders the landing page and handles any landing page logic.
It also receives the text messages and decides what to do in response.
The primary things it does in response to text messages include:
* calls function that adds the text message to the user's journal document; and then send a response message that confirms the message has been received and what the user's streak is
* sends information or links back (in the case of commands being sent (denoted by "-" prefix ie. "-help"))

### schedule_q.py
This is the file scheduled to run every half hour by the server's task scheduler.
It sends out text messages to whoever is set to receive them at each half hour increment.

## Function Files (The functions within these files are mostly self explanatory based on the function names)

### drive_functions.py

### journal_doc_functions.py

### msg_functions.py

### time_functions.py

### signup.py (probably should be renamed as "signup_functions.py" for consistency)

## Misc Files

### client_data.csv
Contains client contact data (phone, email, nickname) as well as other client metadata (morning question streak, custom journal prompt, timezone etc.)
This file is constantly read in and updated and overwritten.

### client_data.ipynb
Jupyter notebook which I use for manual updates to client_data.csv (like adding a new column or changing a single value) and as a general testing ground for other code.

### config.py
Mostly contains secret API keys.
Also contains other misc strings to be imported into files to make it easy to change in that one spot vs changing the string everywhere it is used (ie. working directory file path)