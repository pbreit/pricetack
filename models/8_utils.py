# -*- coding: utf-8 -*-
import datetime
import re
import socket
import unicodedata

arg0 = request.args(0)
arg1 = request.args(1)

def short_date(date):
    return date.strftime('%b %d')

def is_store():
    sub_domain = request.env.http_host.split('.')[0]
    if session.store_name and sub_domain==session.store_name:
        return True
    store = db(db.auth_user.name==sub_domain).select(db.auth_user.header, db.auth_user.name).first()
    if store:
        session.store_name = store.name
        return True
    return False

def page_header():
#    store = db(db.auth_user.name==sub_domain).select(db.auth_user.header).first()
#    if store and store.header:
#        return XML(store.header)
    stripe = DIV(_class='stripe')
    logo = DIV(A(IMG(_src=URL('static', 'images/logo-beta.png'), _width='283', _height='62'), _href=URL('default', 'index')), _id='logo')
    return XML('%s%s' % (user_bar(), logo))

def get_seller():
    'determine if sub-domain or var indicates a seller page'
    seller = row = None
    if request.vars.seller:
        row = db(db.auth_user.name==request.vars.seller).select().first()
    elif request.env.http_host.split('.')[0]:
        row = db(db.auth_user.name==request.env.http_host.split('.')[0]).select().first()
    if row:
        seller = row.name
    return seller

def is_bot(req):
    if not req.env.http_user_agent or len(req.env.http_user_agent)<5:
        return True
    bots = ('Googlebot', 'msnbot', 'Baiduspider', 'Yahoo', 'YandexBot')
    for bot in bots:
        if re.search(bot, req.env.http_user_agent):
            return True
    return False

def is_pricetack():
    if request.env.http_host.split('.')[0].split(':')[0] in ['pricetack', 'test', 'pb-dev', 'localhost']:
        return True
    return False

def user_bar():
    action = URL('default', 'user')
    if auth.user:
        logout=A('logout', _href=action+'/logout')
        profile=A('profile', _href=action+'/profile')
        password=A('change password', _href=action+'/change_password')
        bar = SPAN(auth.user.email, ' | ', profile, ' | ', password, ' | ', logout, _class='auth_navbar')
    else:
        login=A('login', _href=action+'/login')
        register=A('register',_href=action+'/register')
        lost_password=A('lost password', _href=action+'/request_reset_password')
        bar = SPAN(' ', login, ' | ', register, ' | ', lost_password, _class='auth_navbar')
    return bar

def seller_bar(session, item):
    bar = ''
    if auth.user and auth.user.id==item.seller:
        if item.status in ['active']:
            edit = A('edit item', _href=URL('manage', 'item', args=item.id))
            cancel = A('cancel item', _href=URL('manage', 'cancel', args=item.id))
            copy = A('copy item', _href=URL('manage', 'item', vars={'ref': item.id}))
            bar = '%s | %s | %s' % (edit, cancel, copy)
        if item.status in ['canceled', 'expired']:
            relist = A('relist item', _href=URL('manage', 'item', vars={'relist': item.id}))
            copy = A('copy item', _href=URL('manage', 'item', vars={'ref': item.id}))
            archive = A('archive item', _href=URL('manage', 'archive', args=item.id))
            bar = '%s | %s | %s' % (relist, copy, archive)
    if bar:
        return DIV(XML(bar), _class="edit-item-btn")
    else:
        return ''

#set up logging
def _init_log():
    import os,logging,logging.handlers,time
    logger = logging.getLogger(request.application)
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(os.path.join(
        request.folder,'private','applog.log'),'a',1024*1024,1)
    handler.setLevel(logging.INFO) #or DEBUG
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(filename)s %(lineno)d %(funcName)s(): %(message)s'))
    logger.addHandler(handler)
    return logger

app_logging = cache.ram('app_wide_log',lambda:_init_log(),time_expire=None)

#encode/decode id
ed_ALPHABET = "bcdfghjklmnpqrstvwxyz0123456789BCDFGHJKLMNPQRSTVWXYZ"
ed_BASE = len(ed_ALPHABET)
ed_MAXLEN = 6

def encode_id(self, n):

    pad = self.MAXLEN - 1
    n = int(n + pow(self.BASE, pad))

    s = []
    t = int(math.log(n, self.BASE))
    while True:
        bcp = int(pow(self.BASE, t))
        a = int(n / bcp) % self.BASE
        s.append(self.ed_ALPHABET[a:a+1])
        n = n - (a * bcp)
        t -= 1
        if t < 0: break

    return "".join(reversed(s))

def decode_id(self, n):

    n = "".join(reversed(n))
    s = 0
    l = len(n) - 1
    t = 0
    while True:
        bcpow = int(pow(self.BASE, l - t))
        s = s + self.ed_ALPHABET.index(n[t:t+1]) * bcpow
        t += 1
        if t > l: break

    pad = self.MAXLEN - 1
    s = int(s - pow(self.BASE, pad))

    return int(s)
