from datetime import timedelta

from django.core.mail import EmailMessage,send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from pyotp import TOTP
from twilio.rest import Client
from ConnectionHub import settings

import smtplib

import secrets
import base64


class OtpVerification(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    otp = models.CharField(max_length=6, blank=True)
    type = models.CharField(max_length=10, choices=(('email', 'Email'), ('phone', 'Phone')))
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def generate_otp_secret_key(self, length=6):
    # Generate random bytes using a cryptographically-secure random number generator
         random_bytes = secrets.token_bytes(length)

    # Encode the random bytes in Base32 to get the OTP secret key
         otp_secret_key = base64.b32encode(random_bytes).decode('utf-8')

         return otp_secret_key


    def __str__(self):
        return f"OTP of {self.username}"

    def generate_otp(self):
        otp_secret_key = self.generate_otp_secret_key(length=6)
        print(otp_secret_key )
        self.otp = TOTP(otp_secret_key).now()
       
        print(self.otp)
        self.save()

    def send_otp(self):
        if not self.otp:
            self.generate_otp()
        subject = 'OTP Validation of ConnectionHub'
        html_message = render_to_string(
            'otp-email.html',
            {
                'otp': self.otp,
                'name': self.username
            }
        )
   
        if self.type == 'email':
            message = EmailMessage(
                subject=subject,
                body=html_message,
                to=[self.email],
            )
         
            # message.content_subtype = 'html'
         
            # print("send otp module 1111111111")
            # message.send()
           
            try:
                send_mail("h","jjj", self.email, [self.email])
            except :
               print("Error sending email:")
           
            print("send otp module3333333333")


        # else:
        #     TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
        #     TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
        #     client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        #     verification = client.verify.v2.services(TWILIO_ACCOUNT_SID) \
        #         .verification \
        #         .create(to=self.phone_number, channel="sms")

    def verify_otp(self):
        current_date = timezone.now()
        if (self.created_at + timedelta(minutes=5)) > current_date:
            self.verified = True
            self.save()
            return True
        return False
