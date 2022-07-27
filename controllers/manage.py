# -*- coding: utf-8 -*-
from decimal import *

def index():
    return dict()

@auth.requires_login()
def orders():
    if arg0 not in ['new', 'shipped']:
        redirect(URL('manage', 'orders', args='new'))
    return dict()

def item_validation(form):
    if ((Decimal(form.vars.drops) * form.vars.price_change) / form.vars.start_price) < 0.2:
        form.errors.start_price = form.errors.drops = form.errors.price_change = 'must decrease by at least 20%'
    if form.vars.shipping_amount > 6.0:
        if form.vars.shipping_amount > (form.vars.start_price * Decimal('0.2')):
            form.errors.shipping_amount = 'max $6.00 or 20% of item'

@auth.requires_login()
def item():
    shipping_method = 1
    item = ref_item = None
    item_id = request.args(0) or request.vars.relist or None
    if str(item_id).isdigit():
        item = db.item(item_id)
        if not item:
            session.flash = 'Item not found'
            redirect(URL('manage', 'index'))
        if item and auth.user_id != item.seller:
            session.flash = 'Only creator may edit'
            redirect(URL('manage', 'index'))
        form = SQLFORM(db.item, item)
        shipping_method = item.shipping_method
        request.vars.image_display = item.image_display
    else:
        form = SQLFORM(db.item)
        if request.vars.ref:
            ref_item = db.item(request.vars.ref)
            if ref_item and ref_item.seller!=auth.user.id:
                ref_item = dict()
        else:
            ref_item = dict()
        if ref_item:
            form.vars = copy_item_vars(ref_item, form.vars)
            shipping_method = ref_item.shipping_method
            request.vars.image_display = ref_item.image_display
    if form.accepts(request, session, onvalidation=item_validation):
        if form.vars.id:
            item = db.item(form.vars.id)
            if item.status in ['canceled', 'expired']:
                item.update_record(status='active', start_date=request.now)
                update_watchlist(item.id, 'active')
        if ref_item:
            item = db.item(form.vars.id)
            item.update_record(image=ref_item.image)
        session.flash = 'Item saved'
        redirect(URL('default', 'item', args='%s-%s' % (slugify(form.vars.title, maxlen=50), form.vars.id)))
    elif form.errors:
        app_logging.info(form.errors)
        response.flash = 'missing or invalid values'
    return dict(form=form, item=item, shipping_method=shipping_method)

@auth.requires_login()
def items():
    if arg0 not in ['active', 'sold', 'canceled', 'expired']:
        redirect(URL('manage', 'items', args='active'))
    return dict()

@auth.requires_login()
def order():
    row = db((db.purchase.id==request.args(0)) &
            (db.item.id==db.purchase.item) &
            (db.item.seller==auth.user.id)).select().first()
    form = SQLFORM.factory(Field('shipping_number'))
    if form.accepts(request, session):
        row.item.update_record(status='shipped')
        row.purchase.update_record(status='shipped', ship_date=request.now,
                shipping_number=form.vars.shipping_number)
        update_watchlist(row.item.id, 'sold')
        context = dict(purchase=row.purchase, item=row.item)
        send_email(template='shipped_buyer', recipient=row.purchase.email,
                subject='Item has been shipped', context=context)
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form, row=row)

@auth.requires_login()
def cancel():
    item = db.item(request.args(0))
    if item and auth.user_id != item.seller:
        session.flash = 'Only creator may edit'
        redirect(URL('default', 'item', args=request.args(0)))
    item.update_record(status='canceled')
    update_watchlist(item.id, 'canceled')
    session.flash = 'Item canceled'
    redirect(URL('default', 'item', args=request.args(0)))

@auth.requires_login()
def archive():
    item = db.item(request.args(0))
    if item and auth.user_id != item.seller:
        session.flash = 'Only creator may edit'
        redirect(URL('default', 'item', args=request.args(0)))
    item.update_record(status='archived')
    update_watchlist(item.id, 'archived')
    session.flash = 'Item archived'
    redirect(URL('manage', 'index'))

@auth.requires_login()
def import_items():
    import csv
    form=FORM('Import File:',
            INPUT(_type='file', _name='ifile'),
            INPUT(_type='submit', _value='load file'))
    import_form = FORM(INPUT(_type='submit', _value='import items'))
    if form.accepts(request, session):
        response.flash = 'form accepted'
        f = form.vars.ifile.file
        try:
            reader = csv.DictReader(f)
        except:
            form.errors.file = 'Invalid file'
        else:
            return dict(form=form, import_form=import_form, reader=reader)
    if import_form.accepts(request, session):
        pass
    return dict(form=form, reader=None)

@auth.requires_login()
def html():
    items = db((db.item.seller==auth.user_id) &
            (db.item.status=='active') &
            (db.item.grouping!='test')).select()
    new_items = db((db.item.seller==auth.user_id) &
            (db.item.status=='active') &
            (db.item.grouping!='test')).select(orderby=db.item.start_price)
    reduced_items = db((db.item.seller==auth.user_id) &
            (db.item.status=='active') &
            (db.item.grouping!='test')).select(orderby=~db.item.modified_on)
    expiring_items = db((db.item.seller==auth.user_id) &
            (db.item.status=='active') &
            (db.item.grouping!='test')).select(orderby=db.item.expire_date)
    return dict(items=items)

def stripe():
    auth_service = db((db.auth_service.auth_user==auth.user_id) &
            (db.auth_service.name=='stripe') &
            (db.auth_service.status=='active')).select().last()
    db.auth_service.name.writable = False
    form = SQLFORM(db.auth_service, auth_service)
    form.vars.name = 'stripe'
    if form.accepts(request, session):
        session.flash = 'API Key saved'
        redirect(URL('stripe', 'index'))
    elif form.errors:
        response.flash = 'Error saving API Key'
    return dict(form=form)

def payment_options():
    import urllib, json
    uri = 'https://54676ecc296a11e2a861026ba7d31e6f:@api.balancedpayments.com/v1/marketplaces/TEST-MP2zt9kgChN8UICXWw6zDkyc'
    if request.args(0)=='setup':
        params = urllib.urlencode({'name': 'BofA', 'account_number': '11111111', 'bank_code': '121000358'})
        result = json.loads(urllib.urlopen('%s/bank_accounts' % uri, params).read())
        app_logging.info(result)
        params = urllib.urlencode({'email_address': 'merchant@pricetack.com', 'bank_account_uri': result['uri'],
            'merchant[type]': 'person', 'merchant[name]': 'Joe Merchant', 'merchant[street_address]': '333 Grant Ave',
            'merchant[postal_code]': '94108', 'merchant[country]': 'USA', 'merchant[dob]': '1970-03',
            'merchant[phone_number]': '4156377864'})
        result = json.loads(urllib.urlopen('%s/accounts' % uri, params).read())
        app_logging.info(result)
        db.auth_service.insert(auth_user=auth.user_id, name='balanced', username=result['id'], status='active')
        redirect(URL('manage', 'payment_options'))
    auth_service = db((db.auth_service.auth_user==auth.user_id) &
            (db.auth_service.name=='balanced') &
            (db.auth_service.status=='active')).select().last()
    if auth_service:
        return dict(auth_service=auth_service)
    else:
        return dict(auth_service=None)

    return dict(form=form)

def copy_item_vars(ref_item, form_vars):
    form_vars.title = ref_item.title
    form_vars.start_price = ref_item.start_price
    form_vars.currency = ref_item.currency
    form_vars.drops = ref_item.drops
    form_vars.price_change = ref_item.price_change
    form_vars.duration = ref_item.duration
    form_vars.shipping_amount = ref_item.shipping_amount
    form_vars.grouping = ref_item.grouping
    form_vars.description = ref_item.description
    form_vars.is_local = ref_item.is_local
    form_vars.auto_relist = ref_item.auto_relist
    form_vars.hide_schedule = ref_item.hide_schedule
    return form_vars