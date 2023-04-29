import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)


def send_sms(content):
    message = client.messages \
        .create(
        body=f'{content}\n',
        from_='+13152903312',
        to='+44 7751 174873'
    )
