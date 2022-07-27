# -*- coding: utf-8 -*- 

db.define_table('watchlist',
    Field('item', db.item),
    Field('email'),
    Field('status', default='active'),
    Field('send_date', 'datetime'),
    Field('source', default=session.src),
    Field('referer', default=session.referer),
    record_signature)

def update_watchlist(item, status='inactive'):
    watchlists = db(db.watchlist.item==item).select()
    for watchlist in watchlists:
        watchlist.update_record(status=status)
