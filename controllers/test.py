# -*- coding: utf-8 -*-

def index():
    rows = db(db.item.id<20).select()
    return dict(rows=rows)
