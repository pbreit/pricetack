# -*- coding: utf-8 -*-

def item_filter():
    count = int(request.vars.count or settings.items_per_page)
    page = int(request.vars.page or 1)
    limitby = ((page-1)*count, (page*count)+1)

    if request.vars.sort=='newest':
        orderby = ~db.item.start_date
    elif request.vars.sort=='expiring':
        orderby = db.item.expire_date
    else:
        orderby = ~db.item.modified_on

    if request.vars.grouping:
        query = db.item.grouping==request.vars.grouping
    else:
        query = db.item.grouping!='test'

    if request.vars.seller:
        if request.vars.seller.isdigit():
            seller_id = request.vars.seller
        else:
            seller_id = db(db.auth_user.name==request.vars.seller).select(db.auth_user.id).first()
        query = query & (db.item.seller==seller_id)

    status = request.vars.status or 'active'
    query = query & (db.item.status==status)
    items = db(query).select(orderby=orderby, limitby=limitby)
    return dict(items=items, page=page, count=count)

def order_summary():
    seller = None
    purchase = None
    item = db.item(request.args(0))
    if item:
        seller = db(db.auth_user.id==item.seller).select(db.auth_user.name).first()
        purchase = db((db.purchase.item==item.id) &
            (db.purchase.status.belongs(['new', 'shipped']))).select().last()
    return dict(item=item, seller=seller, purchase=purchase)

def manage_orders():
    status = arg0 or 'new'
    orders = db((db.item.seller==auth.user_id) &
            (db.purchase.item==db.item.id) &
            (db.purchase.status==status)).select(orderby=~db.item.created_on)
    return dict(status=status, orders=orders)

def manage_items():
    status = arg0 or 'active'
    left = db.listing.on((db.item.id==db.listing.item)&(db.listing.status=='active'))
    items = db(db.item.seller==auth.user_id)(db.item.status==status).select(
            db.item.ALL, db.listing.ALL, left=left, orderby=~db.item.created_on)
    return dict(status=status, items=items)

def item_groupings():
    seller = db(db.auth_user.name==request.args(0)).select().first()
    if seller:
        groupings = db((db.item.status=='active') &
            (db.item.seller==seller) &
            (db.item.grouping!='test')).select(db.item.grouping,
                orderby=db.item.grouping, distinct=True)
        return dict(groupings=groupings)
    groupings = db((db.item.status=='active') &
        (db.item.grouping!='test')).select(db.item.grouping,
            orderby=db.item.grouping, distinct=True, cache=(cache.ram, 600))
    return dict(groupings=groupings)
