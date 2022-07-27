# -*- coding: utf-8 -*-

def index():
    items = {}
    count = int(request.vars.count or settings.items_per_page)
    format = request.vars.format or 'list'
    page = int(request.vars.page or 1)
    limitby = ((page-1)*count, (page*count)+1)
    
    if request.vars.orderby=='expiring':
        orderby = db.item.expire_date
    elif request.vars.orderby=='newest':
        orderby = ~db.item.start_date
    else:
        orderby = ~db.item.modified_on

    if not request.vars:
        items = db((db.item.status=='active') &
                (db.item.grouping!='test')).select(orderby=orderby, limitby=limitby)
        return dict(items=items, page=page, count=count)

    query = "grouping!='test'"
    
    if request.vars.status in []:
        query += " AND status='%s'" % request.vars.status
    else:
        query += " AND status='active'"

    if request.vars.seller:
        if request.vars.seller.isdigit():
            seller_id = request.vars.seller
        else:
            seller_id = db(db.auth_user.name==request.vars.seller).select(db.auth_user.id).first()
        if seller_id:
            query += " AND created_by=%d" % seller_id

    search_term = request.vars.q
    if search_term:
        if request.is_local:
            query += " AND title LIKE '%%%s%%'" % search_term
        else:
            search_term = ' & '.join(search_term.split(' '))
            query += " AND to_tsvector('english', title) @@ to_tsquery('english', '%s')" % search_term

    items = db(query).select(db.item.ALL, orderby=orderby, limitby=limitby)
    
    return dict(items=items, page=page, count=count)
