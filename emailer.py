#!/usr/bin/env python
# encoding: utf-8
# This script is modified from http://robertwdempsey.com/python3-email-with-attachments-using-gmail/
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#note: If needed, this website teaches how to attach pictures in-line with the email body.
#http://code.activestate.com/recipes/473810-send-an-html-email-with-embedded-image-and-plain-t/


class Emailer():
    def __init__(self, config):
        self.address = config['email']['address']
        self.password = config['email']['password']

    def send(self, recipients=[], cc=[], bcc=[], subject='', message='', attachments=[]):
        sender = self.address
        gmail_password = self.password
        COMMASPACE = ', '
        _recipients = recipients
        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer['Subject'] = subject
        outer['To'] = COMMASPACE.join(_recipients)
        outer['From'] = sender
        outer['CC'] = COMMASPACE.join(cc)
        #bcc is not added here, because we don't want recipients to know who we sent them to. bcc will be added later with _recipients in s.sendmail()
        outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
        # List of attachments
        _attachments = attachments #['FULL PATH TO ATTACHMENTS HERE']

        _message = message
        outer.attach(MIMEText(_message, 'plain'))

        # Add the attachments to the message
        for file in _attachments:
            try:
                with open(file, 'rb') as fp:
                    msg = MIMEBase('application', "octet-stream")
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
                outer.attach(msg)
            except:
                print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
                raise

        composed = outer.as_string()

        # Send the email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(sender, gmail_password)
                s.sendmail(sender, _recipients+cc+bcc, composed)
                s.close()
            print("Email sent!")
        except:
            print("Unable to send the email. Error: ", sys.exc_info()[0])
            raise
    def get_template(self, template_directory):
        #Reads from a pre-written txt file and changes it into a string for the body of email
        string = ''
        f = open(template_directory,'r')
        while True:
            buffer = f.readline()
            if buffer == '':
                f.close()
                return string
            else:
                string += buffer











