import config
from client_data_functions import get_client_data, put_client_data
from sign_up_functions import create_new_user
import stripe
# from flask import request, session, redirect

stripe.api_key = config.stripe_api_key



def stripe_create_customer():

    name = request.form.get('name')
    phone = int(request.form.get('phone'))
    stripeToken = request.form.get('stripeToken')

    customer = stripe.Customer.create(
        name=name,
        email=session['user']['email'],
        phone=phone,
        payment_method = stripeToken
    )
    session['stripe_customer_id'] = customer['id']

    sign_up(session['user']['email'], customer['phone'], customer['name'])

    #add stripe information to customer row in client_data
    client_data = get_client_data()
    client_data.loc[(client_data.email == session['user']['email']), ('stripe_customer_id')] = session['stripe_customer_id']
    client_data.loc[(client_data.email == session['user']['email']), ('stripe_payment')] = stripeToken
    put_client_data(client_data)

    # return jsonify(customer)
    return redirect('/successful_sign_up')


# @application.route('/stripe-charge-customer', methods=['GET'])
# def charge():
#     try:
#         stripe.PaymentIntent.create(
#             amount=50, #amount in cents $10 == 1000
#             currency='usd',
#             # customer='{{CUSTOMER_ID}}',
#             customer = CUSTOMER_ID,
#             off_session=True,
#             confirm=True,
#             payment_method = PAYMENT_METHOD
#         )
#         print('successful charge')
#     except stripe.error.CardError as e:
#         err = e.error
#         # Error code will be authentication_required if authentication is needed
#         print("Code is: %s" % err.code)
#         payment_intent_id = err.payment_intent['id']
#         payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
#         return jsonify(payment_intent)

# @application.route('/create-checkout-session', methods=['POST', 'GET'])
# def create_checkout_session():
#     # if request.method == "POST":

#     # #test
#     # print(session['user']['given_name'])

#     #create new entry in client_data with prospect's data
#     auth_data(session['user']['email'], session['phone'], session['user']['given_name'])
#     print('auth data function called')

#     #create stripe customer and save customer ID for creating their billing portal
#     stripe_customer =  stripe.Customer.create(
#     email=session['user']['email'],
#     phone=int(session['phone'])
#     )
#     print('stripe_customer created')

#     session['stripe_customer_id'] = stripe_customer['id']

#     print('stripe_customer_id added to session')
#     print('stripe_customer_id: ' + session['stripe_customer_id'])

#     PRICE_ID = 'price_1LRJHZA4W6hAG7MTfRjlyMBR'

#     try:
#         # # gets price id in alternative way for testing purposes
#         # prices = stripe.Price.list(
#         #     lookup_keys=[request.form['lookup_key']],
#         #     expand=['data.product']
#         # )
#         # PRICE_ID = prices.data[0].id

#         checkout_session = stripe.checkout.Session.create(
#             customer = session['stripe_customer_id'],
#             line_items=[
#                 {
#                     'price': PRICE_ID,
#                     'quantity': 1,
#                 },
#             ],
#             mode='subscription',
#             success_url=domain +
#             '/successful_sign_up',
#             cancel_url=domain + '/',
#         )

#         return redirect(checkout_session.url, code=303)

#     except Exception as e:
#         print(e)
#         print("error in create checkout session")
#         return "Server error", 500

# @application.route('/webhook', methods=['POST'])
# def webhook_received():
#     print("webhook received route is triggered")

#     checkout_completed_wh_secret = config.checkout_completed_wh_secret
#     request_data = json.loads(request.data)

#     if checkout_completed_wh_secret:
#         # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
#         signature = request.headers.get('stripe-signature')
#         try:
#             event = stripe.Webhook.construct_event(
#                 payload=request.data, sig_header=signature, secret=checkout_completed_wh_secret)
#             stripe_customer_id = event['data']['object']['customer']
#             email = event['data']['object']['customer_details']['email']

#         except Exception as e:
#             return e
#         # Get the type of webhook event sent - used to check the status of PaymentIntents.
#         event_type = event['type']
#     else:
#         data = request_data['data']
#         event_type = request_data['type']


#     print('event ' + event_type)


#     if event_type == 'checkout.session.completed':
#         print('🔔 Payment succeeded!')

        # client_data = get_client_data()
#         #Replace value in an entry
#         client_data.loc[client_data.email == email ,'stripe_customer_id']=stripe_customer_id
#         client_data.loc[client_data.email == email ,'account_active']= 'y'
#         #sign_up date
#         now=datetime.today()
#         date_str = now.strftime("%m/%d/%y")
#         client_data.loc[client_data.email == email ,'sign_up_date']=date_str
        # put_client_data(client_data)


#         print("calls sign_up function")
#         sign_up(email)


#     return jsonify({'status': 'success'})



# @application.route('/create-customer-portal-session', methods=['POST'])
# def customer_portal():
#     stripe_customer_id = session.get('stripe_customer_id')

#     # Authenticate your user.
#     stripe_session = stripe.billing_portal.Session.create(
#         customer=stripe_customer_id,
#         return_url=domain,
#   )
#     return redirect(stripe_session.url)

