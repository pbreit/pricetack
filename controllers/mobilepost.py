# -*- coding: utf-8 -*-
from decimal import *

def index():
    form = SQLFORM.factory(
        Field('username'),
        Field('title'),
        Field('price', 'decimal(17,2)'),
        Field('image', 'upload', uploadfolder=request.folder+'static/uploads'))
    if form.accepts(request.vars):
        app_logging.info(request.vars)
        seller = db(db.auth_user.email==form.vars.username).select(db.auth_user.id).first()
        title = form.vars.title
        start_price = form.vars.price
        price_change = form.vars.price * Decimal('0.1')
        drops = 4
        duration = 7
        item_id = db.item.insert(seller=seller, title=title, start_price=start_price,
            price_change=price_change, drops=drops, duration=duration, image=form.vars.image)
        return str(item_id)
    elif form.errors:
        app_logging.info(form.vars)
        return 'error'
    return 'start'