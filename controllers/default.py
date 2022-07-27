# -*- coding: utf-8 -*-
import re

if not session.referer:
    session.referer = request.env.http_referer

if request.vars.src:
    if not session.src:
        session.src = request.vars.src

def index():
    items = db((db.item.flags.contains('featured')) &
            (db.item.status=='active') &
            (db.auth_user.id==db.item.seller)).select(limitby=(0,4), orderby='<random>')
    return dict(items=items)

def items():
    return dict()

def store():
	return dict()

def item():
    header = buyer_email = ''
    watching = False
    item_id = id_from_slug(request.args(0))
    item = db(db.item.id==item_id).select().first()
    if item:
        if not (item.seller==auth.user_id or is_bot(request)):
            item.update_record(views=item.views+1, modified_on=item.modified_on, modified_by=item.modified_by)
        seller = db.auth_user(item.seller)
        auth_service = None
        auth_service = db((db.auth_service.auth_user==seller.id) &
                (db.auth_service.name=='ebay')).select().first()
        listing = db((db.listing.item==item.id) &
                (db.listing.status=='active') &
                (db.listing.service=='ebay')).select().last()
        if 'buyer_email' in request.cookies:
            buyer_email = request.cookies['buyer_email'].value
            watching = db((db.watchlist.item==item.id) &
                          (db.watchlist.email==buyer_email)).select().first()!=None
        response.title = '%s on Pricetack' % item.title
        return dict(item=item, seller=seller, auth_service=auth_service, listing=listing,
                header=header, watching=watching, buyer_email=buyer_email)
    else:
        session.flash = 'Item not found'
        redirect(URL('index'))

def contact_seller():
    item = db.item(request.args(0))
    seller = db.auth_user(item.seller)
    subject = item.title
    form = SQLFORM.factory(Field('message', 'text', requires=IS_NOT_EMPTY()),
            Field('reply_to', requires=IS_NOT_EMPTY()),
            Field('msg_type'))
    if 'buyer_email' in request.cookies:
        form.vars.reply_to = request.cookies['buyer_email'].value
    if form.process().accepted:
        if form.vars.msg_type:
            redirect(URL('default', 'item', args=item.slug))
        send_email(template='contact_seller', recipient=seller.email,
                reply_to=form.vars.reply_to, subject=subject,
                context=dict(item=item, message=form.vars.message,
                reply_to=form.vars.reply_to))
        session.flash = 'Message sent'
        redirect(URL('default', 'item', args=item.slug))
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form, item=item, seller=seller.name, subject=subject)

def user():
    form = auth()
    auth.messages.reset_password = \
            'Click on the link https://' + request.env.http_host + \
            URL('default','user',args=['reset_password']) + \
            '/%(key)s to reset your password'
    if auth.user:
        response.cookies['login_email'] = auth.user.email
        response.cookies['login_email']['expires'] = 24 * 3600
        response.cookies['login_email']['path'] = '/'
    if 'login_email' in request.cookies and request.args(0) in ['login', 'request_reset_password']:
        form.element(_name='email').update(_value=request.cookies['login_email'].value)
    return dict(form=form)

def main_sitemap():
    lastmod='2011-08-01'
    changefreq='monthly'
    priority='0.6'
    urls = ['index', 'about', 'learn-more']
    return dict(urls=urls, lastmod=lastmod, changefreq=changefreq, priority=priority)

def blog():
    if request.args(0)=='rss':
        redirect('http://pricetack.tumblr.com/rss')
    redirect('http://pricetack.tumblr.com')

def mobilepost():
    item_id = 0
    form = SQLFORM.factory(
        Field('username'),
        Field('password'),
        Field('title'),
        Field('price'),
        Field('image', 'upload', uploadfolder=request.folder+'static/uploads'))
    app_logging.info(request.vars)
    if form.accepts(request):
        app_logging.info(form.vars.title)
        user = db(db.auth_user.email==form.vars.username).select().first()
        if user:
            item_id = db.item.insert(seller=user, title=form.vars.title,
                image=form.vars.image_newfilename,
                start_price=form.vars.price, price_change=form.vars.price * 0.1)
            app_logging.info(item_id)
    elif form.errors:
        response.flash = 'form has errors'
        app_logging.info(form.errors)
    return dict(item_id=2)

def sitemap(): return dict()
def about(): return dict()
def terms(): return dict()
def privacy(): return dict()
def learn_more(): return dict()
def notfound(): return dict()
