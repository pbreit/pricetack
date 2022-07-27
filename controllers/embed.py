# -*- coding: utf-8 -*-

def listings():
    count = int(request.vars.count or 4)
    page = int(request.vars.page or 0)
    limitby = (page*count, (page+1)*count+1)
    orderby = ~db.item.modified_on
    seller = request.vars.seller
    items = db((db.auth_user.name==seller) &
            (db.item.seller==db.auth_user.id) &
            (db.item.status=='active') &
            (db.item.grouping!='test')).select(limitby=limitby, orderby=orderby)
    return dict(items=items, page=page, count=count)