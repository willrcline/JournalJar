#project path
project_working_directory = '/home/willcline/benji'

#flask
flask_secret_key = '!secret'

#twilio
twilio_account_sid = 'AC68279e2192dfd6cc97636821ca37906b'
twilio_auth_token = 'ed5dbd4e74d9c3806a1d451525e80573'
twilio_phone = '+16292496969'

#stripe
stripe_pk_key = 'pk_live_51KPc5RA4W6hAG7MTVWCDIlFNFDYu9MSI6f8nyqHoiKHJvf5xuukppbBW4OL2TTQ9zMK8jfan6EVeShWAqkV9dSR0001TbYN5Xx'
stripe_api_key = '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'
# stripe_api_key = 'sk_test_51KPc5RA4W6hAG7MT0MYJkOKd4f7kMnq2sChz0gZhyE0LtWQc5zTAJuwQ75TPEGTVmHi2YsAwYU0IsGuKogGRyCdk00NLETkTP8'
#webhooks
checkout_completed_wh_secret = 'whsec_7mUDI90npsQIxSecUR0AD8dDlfkZaoW7'

#oauth
GOOGLE_CLIENT_ID = "347619204405-o3dlkb2rg99v005hju2oro0jppou562d.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

#drive
g_drive_CLIENTID = "347619204405-p714ckniqrkoobs03vebteogibv2bnla.apps.googleusercontent.com"
g_drive_CLIENTSECRET = "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"
g_drive_REFRESHTOKEN = "1//04QNiYgESDmT6CgYIARAAGAQSNwF-L9IrDJkmLDAap1JLpwSx9EV-tErRYCLx_szN6A8JvCL0Eo-G8-z79xHSMtH3tbf-z-fFoJI"
#folderID
g_drive_folder_id = r"1X88Pa7CGOzt_cxZQD3wvlC7iTOfn1zrT"

#AWS
aws_access_key_id='AKIATVWG33Z6UKQSV2F7'
aws_secret_access_key='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'
# file paths
aws_bucket_path = "s3://elasticbeanstalk-us-west-2-252746391165"
aws_root_folder = 'ben-storage'
aws_bucket = "elasticbeanstalk-us-west-2-252746391165"
aws_key = aws_root_folder + '/' + 'client_data.csv'
client_data_path = aws_bucket_path + '/' + aws_root_folder + '/' + "client_data.csv"
journal_folder = 'journals'

