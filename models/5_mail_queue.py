# -*- coding: utf-8 -*- 
import re

db.define_table('mail_queue',
    Field('status', default='pending'),
    Field('recipient'),
    Field('sender'),
    Field('reply_to'),
    Field('subject'),
    Field('message', 'text'),
    Field('err_msg', 'text'),
    Field('sent_on', 'datetime'),
    record_signature)

def send_email(queue=False, recipient=settings.email_sender, sender=settings.email_sender,
        reply_to=settings.email_sender, subject='Message from Pricetack',
        message=None, template='generic', context={}):
    if queue:
        body = response.render('emails/%s.html' % template, context)
        try:
            db.mail_queue.insert(
                    status='pending',
                    recipient=recipient,
                    sender=sender,
                    reply_to=reply_to,
                    subject=subject,
                    message=body)
        except Exception as e:
            app_logging.info(e)
            return False
        return True
    else:
        if not message:
            app_logging.info(context)
            message = response.render('emails/%s.html' % template, context)
        try:
            app_logging.info(reply_to)
            result = mail.send(to=recipient, subject=subject, 
                message=message, reply_to=reply_to, bcc=settings.email_bcc)
        except Exception as e:
            app_logging.info(e)
        return result
