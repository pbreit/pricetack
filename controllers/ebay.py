# -*- coding: utf-8 -*- 
import os, urllib, urllib2
from lxml import etree
from ebay import ebay_call
from xml.dom.minidom import parseString

ebayns = '{urn:ebay:apis:eBLBaseComponents}'

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def index():
    auth_service = db((db.auth_service.auth_user==auth.user_id) &
            (db.auth_service.name=='ebay') &
            (db.auth_service.status=='active')).select().last()
    return dict(auth_service=auth_service)

@auth.requires_login()
def link():
    if ebay_environment=='production':
        url = 'https://signin.ebay.com/ws/eBayISAPI.dll'
        runame = 'Pricetack-Pricetac-c87a-4-qygoqbxce'
    else:
        url = 'https://signin.sandbox.ebay.com/ws/eBayISAPI.dll'
        runame = 'Pricetack-Pricetac-3e65-4-fbadbkx'
    data = {'runame': runame}
    result = ebay_call('GetSessionID', environment=ebay_environment, data=data)
    if result:
        app_logging.info(result)
        root = etree.fromstring(result)
        if root.findtext(ebayns+'Ack')=='Success':
            session_id = session.ebay_session_id = root.findtext(ebayns+'SessionID')
            redirect('%s?SignIn&runame=%s&SessID=%s' % (url, runame, session_id))
        else:
            session.flash = 'SessionID error'
            app_logging.info(result)
            redirect(URL('ebay', 'index'))

def accept():
    data = {'session_id': session.ebay_session_id}
    result = ebay_call('FetchToken', environment=ebay_environment, data=data)
    if result:
        app_logging.info(result)
        root = etree.fromstring(result)
        if root.findtext(ebayns+'Ack')=='Success':
            token = root.findtext(ebayns+'eBayAuthToken')
            auth_service = db.auth_service.insert(auth_user=auth.user_id, name='ebay',
                    token=token, status='active', username=request.vars.username)
            session.ebay_session_id = ''
            session.flash = 'Ebay account linked'
            redirect(URL('ebay', 'index'))
        else:
            session.flash = 'SessionID error'
            app_logging.info(result)
            redirect(URL('ebay', 'index'))

def cancel():
    pass

def unlink():
    if request.args(0)=='token':
        if ebay_environment=='production':
            url = 'https://signin.ebay.com/ws/eBayISAPI.dll'
            runame = 'Pricetack-Pricetac-c87a-4-qygoqbxce'
        else:
            url = 'https://signin.sandbox.ebay.com/ws/eBayISAPI.dll'
            runame = 'Pricetack-Pricetac-3e65-4-fbadbkx'
        data = {'runame': runame}
        result = ebay_call('RevokeToken', environment=ebay_environment, data=data)
        if result:
            app_logging.info(result)
            root = etree.fromstring(result)
            if root.findtext(ebayns+'Ack')=='Success':
                session_id = session.ebay_session_id = root.findtext(ebayns+'SessionID')
                redirect('%s?SignIn&runame=%s&SessID=%s' % (url, runame, session_id))
            else:
                session.flash = 'SessionID error'
                app_logging.info(result)
                redirect(URL('ebay', 'index'))
    else:
        auth_service = db((db.auth_service.auth_user==auth.user_id) &
                (db.auth_service.name=='ebay') &
                (db.auth_service.status=='active')).select().last()
        if auth_service:
            auth_service.update_record(status='inactive')
            session.flash = 'Ebay account unlinked'
        else:
            session.flash = 'Ebay account not found'
        redirect(URL('ebay', 'index'))

@auth.requires_login()
def api():
    item = db.item(request.args(1))
    if item and auth.user_id!=item.seller:
        session.flash = 'Only creator may edit'
        redirect(URL('default', 'item', args=request.args(1)))
    if request.vars.ebay_category and request.vars.ebay_category.isdigit():
        category = db(db.category.ebay_id==request.vars.ebay_category).select().first()
        if category:
            item.category = category.id
        else:
            cat = db.category.insert(ebay_id=request.vars.ebay_category)
            item.category = cat
    category = db.category(item.category)
    if not category:
        session.flash = 'Ebay category required'
        redirect(URL('default', 'item', args=request.args(1)))
    seller = db.auth_user(auth.user_id)
    service = db(db.auth_service.auth_user==seller.id)(db.auth_service.name=='ebay').select().first()
    if not service:
        session.flash = 'User not linked to eBay'
        redirect(URL('default', 'item', args=request.args(1)))
    if request.args(0)in ['list', 'revise']:
        description = response.render('ebay/description.html', dict(item=item))
        app_logging.info(description)
        data = {'title': '%s %s' % (item.title[:50], 't@ck'),
            'price': item.current_price,
            'payment_method': 'PayPal',
            'paypal_email': seller.email,
            'ebay_category': category.ebay_id,
            'quantity': '1',
            'description': description,
            'image_url': URL('static', 'uploads', args=item.image_display, host=request.env.http_host),
            'zip': seller.zip,
            'shipping_amount': item.shipping_amount}
        call_name = 'AddItem'
        if request.args(0)=='revise':
            call_name = 'ReviseItem'
            listing = db(db.listing.item==item.id)(db.listing.status=='active')(db.listing.service=='ebay').select().last()
            data['item_id'] = listing.ref_id
        result = ebay_call(call_name, environment=ebay_environment, token=service.token, data=data)
        if result:
            app_logging.info(result)
            root = etree.fromstring(result)
            if root.findtext(ebayns+'Ack')=='Success':
                if call_name=='AddItem':
                    db.listing.insert(service='ebay', item=item.id, ref_id=root.findtext(ebayns+'ItemID'), status='active')
                session.flash = 'Item listed/revised on eBay'
                redirect(URL('default', 'item', args=item.id))
            else:
                session.flash = 'Parse error'
                app_logging.info(result)
                redirect(URL('default', 'item', args=item.id))
        session.flash = 'Listing error'
        app_logging.info(result)
        redirect(URL('default', 'item', args=item.id))
    elif request.args(0)=='cancel':
        listing = db(db.listing.item==item.id)(db.listing.status=='active')(db.listing.service=='ebay').select().last()
        data = {'ref_id': listing.ref_id}
        result = ebay_call('EndItem', environment=ebay_environment, token=service.token, data=data)
        if result:
            app_logging.info(result)
            root = etree.fromstring(result)
            if root.findtext(ebayns+'Ack')=='Success':
                listing.update_record(status='canceled')
                session.flash = 'Item canceled on eBay'
                redirect(URL('default', 'item', args=item.id))
            else:
                session.flash = 'Parse error'
                redirect(URL('default', 'item', args=item.id))
        session.flash = 'Listing error'
        app_logging.info(result)
        redirect(URL('default', 'item', args=item.id))

def enable_notifications():
    service_user = db(db.auth_service.auth_user==auth.user_id).select().first()
    if service_user.token:
        result = ebay_call('SetNotificationPreferences', token=service_user.token)
        if result:
            app_logging.info(result)
            root = etree.fromstring(result)
            if root.findtext(ebayns+'Ack')=='Success':
                session.flash = 'Notifications enabled'
                redirect(URL('ebay', 'index'))
            else:
                session.flash = 'Error'
                redirect(URL('ebay', 'index'))

def description():
    item_id = request.args(0) or 120
    item = db.item(item_id)
    seller = db.auth_user(item.seller)
    return dict(item=item, seller=seller)

def notify():
    app_logging.info(request.post_vars)
    return dict()

def get_categories():
    data = {'LevelLimit': request.vars.LevelLimit,
            'DetailLevel': request.vars.DetailLevel,
            'ViewAllNodes': request.vars.ViewAllNodes}
    result = ebay_call('GetCategories', environment=ebay_environment, data=data)
    if result:
        root = etree.fromstring(result)
        if root.findtext(ebayns+'Ack')=='Success':
            dom = parseString(result)
            categories = dom.getElementsByTagName('Category')
            for category in categories:
                name = getText((category.getElementsByTagName('CategoryName'))[0].childNodes)
                cat_id = getText((category.getElementsByTagName('CategoryID'))[0].childNodes)
                parent = getText((category.getElementsByTagName('CategoryParentID'))[0].childNodes)
                if category.getElementsByTagName('LeafCategory'):
                    is_leaf = True
                else:
                    is_leaf = False
                if not (category.getElementsByTagName('Virtual') or \
                        category.getElementsByTagName('Expired')):
                    db.ebay_category.insert(name=name, cat_id=cat_id, parent=parent, is_leaf=is_leaf)
            return dict(cnt=len(categories))
        else:
            response.flash = 'ack error'
            return dict(result=result)
    else:
        response.flash = 'result error'

def tools(): return dict()
