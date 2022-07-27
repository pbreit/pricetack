# -*- coding: utf-8 -*-

def index():
    buyer_email = None
    if 'buyer_email' in request.cookies:
        buyer_email = request.cookies['buyer_email'].value
    items = db((db.watchlist.email==buyer_email) &
               (db.item.id==db.watchlist.item)).select(orderby=db.item.title)
    return dict(buyer_email=buyer_email, items=items)

def add():
    if request.vars.item and request.vars.email:
        email = request.vars.email
        item_id = request.vars.item
        if not db((db.watchlist.email==email) &
                (db.watchlist.item==item_id) &
                (db.watchlist.status=='active')).select():
            item = db.item(item_id)
            send_date = item.next_date
            db.watchlist.insert(item=item, email=email, send_date=send_date)
        response.cookies['buyer_email'] = email
        response.cookies['buyer_email']['expires'] = 60 * 60 * 24 * 90 #90 days
        response.cookies['buyer_email']['path'] = '/'
