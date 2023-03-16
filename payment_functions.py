import stripe

def charge(amount, customer_id, payment):
    try:
        stripe.PaymentIntent.create(
            amount=50, #amount in cents $10 == 1000
            currency='usd',
            # customer='{{CUSTOMER_ID}}',
            customer = CUSTOMER_ID,
            off_session=True,
            confirm=True,
            payment_method = PAYMENT_METHOD
        )
        print('successful charge')
    except stripe.error.CardError as e:
        err = e.error
        # Error code will be authentication_required if authentication is needed
        print("Code is: %s" % err.code)
        payment_intent_id = err.payment_intent['id']
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return jsonify(payment_intent)
