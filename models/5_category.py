# -*- coding: utf-8 -*- 

db.define_table('category',
    Field('name'),
    Field('parent'),
    Field('ebay_id'),
    Field('google_id'),
    record_signature)
