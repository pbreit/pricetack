# -*- coding: utf-8 -*- 

db.define_table('listing',
    Field('item', db.item),
    Field('service'),
    Field('ref_id'),
    Field('status'),
    record_signature)

db.listing.service.requires = IS_IN_SET(['ebay'])
db.listing.status.requires = IS_IN_SET(['active', 'canceled'])
