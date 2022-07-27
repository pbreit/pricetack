# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import cgi

def add():
    item_id = session.cart_item = request.args(0)
    item = db.item(item_id)
    auth_service = db((db.auth_service.auth_user==item.seller) &
            (db.auth_service.name.belongs(['stripe', 'google', 'balanced'])) & 
            (db.auth_service.status=='active')).select().last()
    if item.status=='active':
        if auth_service and auth_service.name=='stripe':
            payment_method = 'stripe'
        elif auth_service and auth_service.name=='google':
            payment_method = 'google'
        elif auth_service and auth_service.name=='balanced':
            payment_method = 'balanced'
        else:
            payment_method = 'paypal'
        return dict(item_id=item_id, payment_method=payment_method)
    else:
        session.flash='Item not available'
        redirect(URL('default', 'item', args=item.id))

def confirm():
    purchase = db.purchase(request.args(0))
    item = db.item(purchase.item)
    if purchase.zip==request.args(1):
        return dict(purchase=purchase, item=item)
    else:
        session.flash='not found'
        redirect(URL('default', 'index'))

def paypal():
    paypal_config = {'user': 'api_api1.pricetack.com',
            'pwd': 'XB7BL398QGV8TVUF',
            'signature': 'AFcWxV21C7fd0v3bYYYRCpSSRl31AWnJaYXZ7Bn0oTNIDoo5Sfzz7lJc',
            'version': '66.0',
            'endpoint': 'https://api-3t.paypal.com/nvp'}
    if request.args(0)=='cancel':
        redirect(URL('checkout', 'cancel', args=request.args(1)))
    elif request.args(0)=='notify':
        app_logging.info(request.body.read())
    elif request.args(0)=='start':
        item = db(db.item.id==session.cart_item).select().first()
        item.update_record(status='pending')
        seller = db(item.seller==db.auth_user.id).select().first()
        session.payee_id = seller.paypal_email or seller.email
        purchase = db.purchase.insert(
                status = 'pending',
                item = item.id,
                currency = item.currency,
                item_amount = item.current_price,
                shipping_amount = item.shipping_amount,
                amount = item.current_price + item.shipping_amount,
                payment_method = 'paypal',
                payee_id = session.payee_id)
        db.commit()
        values = {'USER': paypal_config['user'],
                'PWD': paypal_config['pwd'],
                'SIGNATURE': paypal_config['signature'],
                'VERSION': paypal_config['version'],
                'METHOD': 'SetExpressCheckout',
                'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
                'SUBJECT': session.payee_id,
                'PAYMENTREQUEST_0_AMT': item.current_price + item.shipping_amount,
                'PAYMENTREQUEST_0_CURRENCYCODE': item.currency,
                'PAYMENTREQUEST_0_INVNUM': '%s-%s' % (request.now.microsecond, purchase.id),
                'PAYMENTREQUEST_0_ITEMAMT': item.current_price,
                'PAYMENTREQUEST_0_SHIPPINGAMT': item.shipping_amount,
                'L_PAYMENTREQUEST_0_NAME0': item.title,
                'L_PAYMENTREQUEST_0_AMT0': item.current_price,
                'L_PAYMENTREQUEST_0_QTY0': '1',
                'RETURNURL': 'http://%s/checkout/paypal/return' % (request.env.http_host),
                'CANCELURL': 'http://%s/checkout/paypal/cancel/%s' % (request.env.http_host, item.id),
                'NOTIFYURL': 'http://%s/checkout/paypal/notify' % (request.env.http_host)}
        result = cgi.parse_qs(urllib.request.urlopen(paypal_config['endpoint'], urllib.parse.urlencode(values)).read())
        if result['ACK'][0]=='Success':
            token = result['TOKEN'][0]
            url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_express-checkout&useraction=commit&token='
            redirect('%s%s' % (url, token))
        else:
            return result
    elif request.args(0)=='return':
        values =   {'USER': paypal_config['user'],
                    'PWD': paypal_config['pwd'],
                    'SIGNATURE': paypal_config['signature'],
                    'VERSION': paypal_config['version'],
                    'SUBJECT': session.payee_id,
                    'METHOD': 'GetExpressCheckoutDetails',
                    'TOKEN': request.vars.token}
        result = cgi.parse_qs(urllib.request.urlopen(paypal_config['endpoint'], urllib.parse.urlencode(values)).read())
        app_logging.info(result)
        if result['ACK'][0]=='Success':
            purchase_id = result['PAYMENTREQUEST_0_INVNUM'][0].split('-')[1]
            purchase = db.purchase(purchase_id)
            purchase.update_record(
                    email=result['EMAIL'][0],
                    name=result['PAYMENTREQUEST_0_SHIPTONAME'][0],
                    first_name=result['FIRSTNAME'][0],
                    last_name=result['LASTNAME'][0],
                    street=result['PAYMENTREQUEST_0_SHIPTOSTREET'][0],
                    street2='',
                    city=result['PAYMENTREQUEST_0_SHIPTOCITY'][0],
                    state=result['PAYMENTREQUEST_0_SHIPTOSTATE'][0],
                    zip=result['PAYMENTREQUEST_0_SHIPTOZIP'][0],
                    country=result['PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE'][0],
                    address_status=result['ADDRESSSTATUS'][0],
                    amount=result['PAYMENTREQUEST_0_AMT'][0],
                    tax_amount=result['PAYMENTREQUEST_0_TAXAMT'][0],
                    source=session.src,
                    referer=session.referer)
            values = {'USER': paypal_config['user'],
                    'PWD': paypal_config['pwd'],
                    'SIGNATURE': paypal_config['signature'],
                    'VERSION': paypal_config['version'],
                    'METHOD': 'DoExpressCheckoutPayment',
                    'SUBJECT': session.payee_id,
                    'TOKEN': request.vars.token,
                    'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
                    'PAYMENTREQUEST_0_DESC': 'Order',
                    'PAYMENTREQUEST_0_AMT': result['PAYMENTREQUEST_0_AMT'][0],
                    'PAYMENTREQUEST_0_CURRENCYCODE': result['PAYMENTREQUEST_0_CURRENCYCODE'][0],
                    'PAYMENTREQUEST_0_ITEMAMT': result['PAYMENTREQUEST_0_ITEMAMT'][0],
                    'PAYMENTREQUEST_0_SHIPPINGAMT': result['PAYMENTREQUEST_0_SHIPPINGAMT'][0],
                    'L_PAYMENTREQUEST_0_NAME0': result['L_PAYMENTREQUEST_0_NAME0'][0],
                    'L_PAYMENTREQUEST_0_AMT0': result['L_PAYMENTREQUEST_0_AMT0'][0],
                    'L_PAYMENTREQUEST_0_QTY0': result['L_PAYMENTREQUEST_0_QTY0'][0],
                    'PAYERID': result['PAYERID'][0]}
            app_logging.info(values)
            result = cgi.parse_qs(urllib.request.urlopen(paypal_config['endpoint'], urllib.parse.urlencode(values)).read())
            if result['ACK'][0]=='Success':
                purchase.update_record(status='new',
                        completed_on=request.now,
                        payment_id=result['PAYMENTINFO_0_TRANSACTIONID'][0])
                item = db(db.item.id==purchase.item.id).select().first()
                item.update_record(status='sold')
                context = dict(item=item, purchase=purchase)
                app_logging.info(context)
                send_email(template='sold_seller', recipient=purchase.payee_id,
                        subject='An item has been purchased', context=context)
                send_email(template='sold_buyer', recipient=purchase.email,
                        subject='You have purchased an item', context=context)
                session.flash = 'payment completed'
                redirect(URL('checkout', 'confirm', args=[purchase.id, purchase.zip]))
            else:
                app_logging.info(result)
                session.flash = 'do error'
                return result
        else:
            app_logging.info(result)
            session.flash = 'get error'
            return result
    else:
        pass

def cancel():
    item = db(db.item.id==request.args(0)).select().first()
    item.update_record(status='active')
    session.cart_item = ''
    session.flash = 'Order canceled'
    redirect(URL('default', 'item', args=item.id))

def stripe():
    item = db(db.item.id==session.cart_item).select().first()
    item.update_record(status='pending')
    seller = db(item.seller==db.auth_user.id).select().first()
    if request.vars.stripToken:
        purchase = db.purchase.insert(status = 'pending',
                item = item.id,
                currency = item.currency,
                item_amount = item.current_price,
                shipping_amount = item.shipping_amount,
                amount = item.current_price + item.shipping_amount,
                payment_method = 'stripe')
    form = SQLFORM(db.purchase)
    if form.accepts(request, session):
        purchase.update_record(payment_id=stripeToken)
        #context = dict(item=item, purchase=purchase)
        #send_email(template='sold_seller', recipient=purchase.payee_id, subject='An item has been purchased', context=context)
        #send_email(template='sold_buyer', recipient=purchase.email, subject='You have purchased an item', context=context)
        session.flash = 'payment completed'
        redirect(URL('checkout', 'confirm', args=[purchase.id, purchase.zip]))
    return dict(form=form, item=item)

def balanced():
    item = db(db.item.id==session.cart_item).select().first()
    item.update_record(status='pending')
    seller = db(item.seller==db.auth_user.id).select().first()
    if request.vars.stripToken:
        purchase = db.purchase.insert(status = 'pending',
                item = item.id,
                currency = item.currency,
                item_amount = item.current_price,
                shipping_amount = item.shipping_amount,
                amount = item.current_price + item.shipping_amount,
                payment_method = 'stripe')
    form = SQLFORM(db.purchase)
    if form.accepts(request, session):
        purchase.update_record(payment_id=stripeToken)
        #context = dict(item=item, purchase=purchase)
        #send_email(template='sold_seller', recipient=purchase.payee_id, subject='An item has been purchased', context=context)
        #send_email(template='sold_buyer', recipient=purchase.email, subject='You have purchased an item', context=context)
        session.flash = 'payment completed'
        redirect(URL('checkout', 'confirm', args=[purchase.id, purchase.zip]))
    return dict(form=form, item=item)

def submit():
    import balanced, urllib, json
    uri = 'https://54676ecc296a11e2a861026ba7d31e6f:@api.balancedpayments.com/v1/marketplaces/TEST-MP2zt9kgChN8UICXWw6zDkyc'
    params = urllib.parse.urlencode({'email_address': 'buyer@pricetack.com', 'card_uri': request.vars.uri})
    result = json.loads(urllib.request.urlopen('%s/accounts' % uri, params).read())
    app_logging.info(result)
    params = urllib.parse.urlencode({'amount': 100})
    result = json.loads(urllib.request.urlopen('%s/accounts/%s/holds' % (uri, result['id']), params).read())
    app_logging.info(result)
    redirect(URL('checkout', 'confirm', args=[]))
