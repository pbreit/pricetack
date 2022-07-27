# -*- coding: utf-8 -*-

if not auth.user or auth.user.email!='pb@pricetack.com':
    redirect(URL('default', 'index'))

def index():
    return dict()

def up():
    func = globals()[request.args(0)]
    try:
        result = func()
        return result
    except Exception, e:
        return e

def copy_created_on_to_start_date():
    rows = db(db.item.id>0).select()
    for row in rows:
        row.update_record(start_date=item.created_on)
    return dict(count=len(rows), rows=rows)

def fix_auth_user_created_on(self=None):
    rows = db(db.auth_user.id.belongs(range(7,40))).select()
    for row in rows:
        row.update_record(created_on='2011-04-13 16:14:00', modified_on='2011-04-13 16:14:00')
    return dict(count=len(rows), rows=rows)

def copy_created_by_to_seller():
    rows = db(db.item.id>0).select()
    for row in rows:
        row.update_record(seller=row.created_by, modified_on=row.modified_on, modified_by=row.modified_by)
    return dict(count=len(rows), rows=rows)

def set_item_is_local_false():
    rows = db(db.item.id>0).select()
    for row in rows:
        row.update_record(is_local=False)
    return dict(count=len(rows), rows=rows)

def set_item_auto_relist_true():
    rows = db(db.item.id>0).select()
    for row in rows:
        row.update_record(auto_relist=True)
    return dict(count=len(rows), rows=rows)

def set_item_hide_schedule_false():
    rows = db(db.item.id>0).select()
    for row in rows:
        row.update_record(hide_schedule=False)
    return dict(count=len(rows), rows=rows)

def set_item_hide_schedule():
    rows = db(db.item.id>0).select(db.item.schedule)
    for row in rows:
        row.update_record(hide_schedule=False)
    return dict(count=len(rows), rows=rows)

def set_item_hide_quantity():
    rows = db(db.item.id>0).select(db.item.quantity)
    for row in rows:
        row.update_record(hide_quantity=False)
    return dict(count=len(rows), rows=rows)

def process_display_images():
    rows = db(db.item.id.belongs(range(282,315))).select()
    for row in rows:
        if row.image:
            row.update_record(image_display=resize_image(row.image, (320,320), 'display'))
    return dict(count=len(rows), rows=rows)
