# -*- coding: utf-8 -*- 

db.define_table('auth_service',
    Field('auth_user', db.auth_user, default=auth.user_id, readable=False, writable=False),
    Field('name'),
    Field('username'),
    Field('uid'),
    Field('token', length=4096),
    Field('status', default='active', readable=False, writable=False),
    record_signature)
