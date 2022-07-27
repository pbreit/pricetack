# -*- coding: utf-8 -*-
import urllib2
from base64 import b64encode
from lxml import etree

google_config = {'merchant_id': '354141213180500',
        'merchant_key': '9-xpmUX_xCCaK1vROxwTcw',
        'production_url': 'https://checkout.google.com/api/checkout/v2/merchantCheckout/Merchant/',
        'sandbox_url': 'https://sandbox.google.com/checkout/api/checkout/v2/merchantCheckout/Merchant/'}

def google():
    if request.args(0)=='cancel':
        redirect(URL('checkout', 'cancel', args=request.args(1)))
    elif request.args(0)=='start':
        item = db(db.item.id==session.cart_item).select().first()
        item.update_record(status='pending')
        seller = db((db.auth_user.id==item.seller)&
                (db.auth_service.auth_user==db.auth_user.id)&
                (db.auth_service.name=='google')&
                (db.auth_service.status=='active')).select().last()
        merchant_id = seller.auth_service.uid
        merchant_key = seller.auth_service.token
        purchase = db.purchase.insert(
                status = 'pending',
                item = item.id,
                currency = item.currency,
                item_amount = item.current_price,
                shipping_amount = item.shipping_amount,
                amount = item.current_price + item.shipping_amount,
                payment_method = 'google',
                payee_id = merchant_id)
        db.commit()
        values = {'item_name': item.title,
                'item_description': '',
                'unit_price': item.current_price,
                'currency': item.currency,
                'quantity': '1',
                'flat_rate_shipping', item.shipping_method_name,
                'shipping_price': item.shipping_amount}
        xml = google_xml('checkout-shopping-cart', values)
        result = call_google(uid, token, xml)
        root = etree.fromstring(result)
        if root.findtext('redirect-url'):
            url = root.findtext('redirect-url')
            redirect(url)
        else
            return result
    elif request.args(0)=='notify':
        app_logging.info(request.body.read())
        values =   {'USER': paypal_config['user'],
                    'PWD': paypal_config['pwd'],
                    'SIGNATURE': paypal_config['signature'],
                    'VERSION': paypal_config['version'],
                    'SUBJECT': session.payee_id,
                    'METHOD': 'GetExpressCheckoutDetails',
                    'TOKEN': request.vars.token}
        result = cgi.parse_qs(urllib.urlopen(paypal_config['endpoint'], urllib.urlencode(values)).read())
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
            result = cgi.parse_qs(urllib.urlopen(paypal_config['endpoint'], urllib.urlencode(values)).read())
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

def google_xml(call_name, data):
    if call_name == 'checkout-shopping-cart':
        return checkout_shopping_cart_xml % data

def call_google(merchant_id, merchant_key, xml):
    auth_hash = b64encode('%s:%s' % (merchant_id, merchant_id))
    headers = ['Authorization': 'Basic %s' % auth_hash,
            'Content-Type': 'application/xml; charset=UTF-8',
            'Accept': 'application/xml; charset=UTF-8']
    body = '%s\n%s' % (xml_header, xml)
    url = '%s/%s' % (google_config['production_url'], merchant_id)
    req = urllib2.Request(url, xml, headers)
    try:
        response = urllib2.urlopen(req)
    except Exception, e:
        return e
    result = response.read()
    return result

checkout_shopping_cart_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<checkout-shopping-cart xmlns="http://checkout.google.com/schema/2">
  <shopping-cart>
    <items>
      <item>
        <item-name>%(item_name)s</item-name>
        <item-description></item-description>
        <unit-price currency="%(currency)s">%(unit_price)s</unit-price>
        <quantity>%(quantity)s</quantity>
      </item>
    </items>
  </shopping-cart>
  <checkout-flow-support>
    <merchant-checkout-flow-support>
      <shipping-methods>
        <flat-rate-shipping name="%(shipping_method)s">
          <price currency="%(currency)s">%(shipping_amount)s</price>
        </flat-rate-shipping>
      </shipping-methods>
    </merchant-checkout-flow-support>
  </checkout-flow-support>
</checkout-shopping-cart>'''

# create shopping cart response
'''
<?xml version="1.0" encoding="UTF-8"?>
<checkout-redirect xmlns="http://checkout.google.com/schema/2"
   serial-number="981283ea-c324-44bb-a10c-fc3b2eba5707">
  <redirect-url>
    https://checkout.google.com/view/buy?o=shoppingcart&amp;shoppingcart=8572098456
  </redirect-url>
</checkout-redirect>
'''

# error response
'''
<?xml version="1.0" encoding="UTF-8"?>
<error xmlns="http://checkout.google.com/schema/2"
    serial-number="3c394432-8270-411b-9239-98c2c499f87f">
    <error-message>Bad username and/or password for API Access.</error-message>
</error>
'''