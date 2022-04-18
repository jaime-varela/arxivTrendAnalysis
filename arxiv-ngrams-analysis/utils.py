# Set of utilities for Arxiv filter and emailer

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendHtmlEmailFromGoogleAccount(toEmail, fromEmail, subject, plainText,htmlText, username,password):
    me = fromEmail
    you = toEmail

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = you

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(plainText, 'plain')
    part2 = MIMEText(htmlText, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    username = username
    password = password

    mail.login(username,password)
    mail.sendmail(me, you, msg.as_string())
    mail.quit()