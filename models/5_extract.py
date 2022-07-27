# -*- coding: utf-8 -*-

db.define_table('image',
    Field('file', 'upload'),
    Field('message_id'),
    Field('email'),
    Field('created_on', 'datetime', default=request.now))

settings.extractor = {
    'username': 'pricetack@gmail.com',
    'password': 'toga1987',
    'pop3_debug': True,
}
