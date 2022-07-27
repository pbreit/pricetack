# -*- coding: utf-8 -*- 

db.define_table('ebay_category',
    Field('name'),
    Field('cat_id', 'integer'),
    Field('parent_id', 'integer'),
    Field('is_leaf', 'boolean'),
    record_signature)
