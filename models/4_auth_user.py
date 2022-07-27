# -*- coding: utf-8 -*-
from gluon.tools import Auth

auth = Auth(db)

record_signature = db.Table(db, 'record_signature',
    Field('created_on', 'datetime', default=request.now,
            writable=False, readable=False),
    Field('created_by', 'integer', default=auth.user_id,
            writable=False, readable=False),
    Field('modified_on', 'datetime', update=request.now,
            writable=False, readable=False),
    Field('modified_by', 'integer', update=auth.user_id,
            writable=False, readable=False))

db.define_table('auth_user',
    Field('first_name', length=128),
    Field('last_name', length=128),
    Field('email', length=128, unique=True),
    Field('password', 'password', length=512, readable=False),
    Field('registration_key', length=512, writable=False, readable=False),
    Field('reset_password_key', length=512, writable=False, readable=False),
    Field('registration_id', length=512, writable=False, readable=False),
    Field('business_name', length=128),
    Field('phone', length=128),
    Field('street', length=128),
    Field('street2', length=128),
    Field('city', length=128),
    Field('state', length=128),
    Field('zip', length=128),
    Field('country', length=128),
    Field('name', length=128, unique=True),
    Field('paypal_email', length=128),
    Field('header', 'text'),
    Field('source', default=session.src, writable=False, readable=False),
    Field('referer', default=session.referer, writable=False, readable=False),
    record_signature)
                                        
auth.settings.hmac_key = 'sha512:8238369f-51df-43c5-939e-42801b5213ab'

db.auth_user.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email),
        IS_NOT_IN_DB(db, db.auth_user.email)]
db.auth_user.password.requires = [IS_STRONG(min=6, special=0, upper=0),
        CRYPT(auth.settings.hmac_key)]
db.auth_user.paypal_email.requires = [IS_EMPTY_OR(IS_EMAIL(error_message=auth.messages.invalid_email))]
db.auth_user.name.requires = IS_EMPTY_OR([IS_SLUG(), IS_LOWER(), IS_LENGTH(minsize=6)])

auth.define_tables()

auth.settings.mailer = mail
auth.settings.create_user_groups = False
auth.settings.login_next = URL('manage', 'index')
auth.settings.logout_next = URL('default', 'index')
auth.settings.profile_next = URL('user', args='profile')
auth.settings.register_next = URL('default', 'learn_more')
auth.settings.retrieve_username_next = URL('index')
auth.settings.retrieve_password_next = URL('index')
auth.settings.change_password_next = URL('index')
auth.settings.request_reset_password_next = URL('user', args='login')
auth.settings.reset_password_next = URL('user', args='login')
auth.settings.verify_email_next = URL('user', args='login')
auth.settings.on_failed_authorization = URL('user', args='on_failed_authorization')

def set_paypal_email(form):
    form.vars.paypal_email=form.vars.email

auth.settings.register_onvalidation.append(lambda form:
        set_paypal_email(form))

auth.settings.register_onaccept.append(lambda form:
        send_email(template='register', recipient=auth.user.email, subject='Thanks for registering'))

auth.settings.profile_onaccept.append(lambda form:
        send_email(template='profile', recipient=auth.user.email, subject='Profile update'))

auth.settings.expiration = 3600
auth.settings.long_expiration = 60*60*24*30
auth.settings.remember_me_form = True

'''
import uuid 
session._salt = session._salt or str(uuid.uuid4())
auth.settings.extra_fields['auth_user'].append(Field('salt',writable=False,readable=False,default=session._salt)) 
auth.define_tables() 
... 
if auth.user: session._salt=auth.user.salt 
db.auth_user.password.requires=CRYPT(auth.settings.hmac_key 
+session._salt)
 '''