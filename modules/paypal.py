# -*- coding: utf-8 -*-
import urllib
import cgi

paypal_config = {'user': 'pricetack_api1.gmail.com',
	             'pwd': 'D4HUALSD4JWMSWR7',
	             'signature': 'AEedYvJ1Eu7u9Di0ZoLUnrmrUZQoANctuMWjBcmOU-ykqP1nKYTamOpF',
	             'version': '66.0',
	             'button_source': '',
	             'endpoint': 'https://api-3t.paypal.com/nvp'}

def set_express_checkout(params, config=paypal_config):
    try:
        values =   {'USER': config['user'],
                    'PWD': config['pwd'],
                    'SIGNATURE': config['signature'],
                    'VERSION': config['version'],
                    'METHOD': 'SetExpressCheckout',
                    'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
                    'SUBJECT': params['SUBJECT'],
                    'PAYMENTREQUEST_0_AMT': params['PAYMENTREQUEST_0_AMT'],
                    'PAYMENTREQUEST_0_CURRENCYCODE': params['PAYMENTREQUEST_0_CURRENCYCODE'],
                    'PAYMENTREQUEST_0_INVNUM': params['PAYMENTREQUEST_0_INVNUM'],
                    'PAYMENTREQUEST_0_ITEMAMT': params['PAYMENTREQUEST_0_ITEMAMT'],
                    'PAYMENTREQUEST_0_SHIPPINGAMT': params['PAYMENTREQUEST_0_SHIPPINGAMT'],
                    'L_PAYMENTREQUEST_0_NAME0': params['L_PAYMENTREQUEST_0_NAME0'],
                    'L_PAYMENTREQUEST_0_AMT0': params['L_PAYMENTREQUEST_0_AMT0'],
                    'L_PAYMENTREQUEST_0_QTY0': params['L_PAYMENTREQUEST_0_QTY0'],
                    'RETURNURL': params['RETURNURL'],
                    'CANCELURL': params['CANCELURL']}
        result = cgi.parse_qs(urllib.urlopen(config['endpoint'], urllib.urlencode(values)).read())
    except:
        pass
    else:
        return result

def get_express_checkout_details(params, config=paypal_config):
    try:
        values =   {'USER': config['user'],
                    'PWD': config['pwd'],
                    'SIGNATURE': config['signature'],
                    'VERSION': config['version'],
                    'SUBJECT': params['payee_id'],
                    'METHOD': 'GetExpressCheckoutDetails',
                    'TOKEN': params['token']}
        result = cgi.parse_qs(urllib.urlopen(config['endpoint'], urllib.urlencode(values)).read())
    except:
        pass
    else:
        return result
        
def do_express_checkout(params, config=paypal_config):
    try:
        values =   {'USER': config['user'],
                    'PWD': config['pwd'],
                    'SIGNATURE': config['signature'],
                    'VERSION': config['version'],
                    'METHOD': 'DoExpressCheckoutPayment',
                    'SUBJECT': params['SUBJECT'],
                    'TOKEN': params['TOKEN'],
                    'PAYMENTREQUEST_0_PAYMENTACTION': params['PAYMENTRREQUEST_0_PAYMENTACTION'],
                    'PAYMENTREQUEST_0_DESC': params['PAYMENTREQUEST_0_DESC'],
                    'PAYMENTREQUEST_0_AMT': params['PAYMENTREQUEST_0_AMT'],
                    'PAYMENTREQUEST_0_CURRENCYCODE': params['PAYMENTREQUEST_0_CURRENCYCODE'],
                    'PAYMENTREQUEST_0_ITEMAMT': params['PAYMENTREQUEST_0_ITEMAMT'],
                    'PAYMENTREQUEST_0_SHIPPINGAMT': params['PAYMENTREQUEST_0_SHIPPINGAMT'],
                    'L_PAYMENTREQUEST_0_NAME0': params['L_PAYMENTREQUEST_0_NAME0'],
                    'L_PAYMENTREQUEST_0_AMT0': params['L_PAYMENTREQUEST_0_AMT0'],
                    'L_PAYMENTREQUEST_0_QTY0': params['L_PAYMENTREQUEST_0_QTY0'],
                    'PAYERID': params['PAYERID']}
        result = cgi.parse_qs(urllib.urlopen(config['endpoint'], urllib.urlencode(values)).read())
    except Exception, e:
        return e
    else:
        pass
