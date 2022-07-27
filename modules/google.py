# -*- coding: utf-8 -*-
import base64

354141213180500:9-xpmUX_xCCaK1vROxwTcw

merchant_id = '354141213180500'
merchant_key = '9-xpmUX_xCCaK1vROxwTcw'
authorization_key = base64.b64encode('%s:%s' % (merchant_id, merchant_key)
http_header = 'Authorization: Basic %s' % authorization_key
Content-Type = 'application/xml; charset=UTF-8'
Accept = 'application/xml; charset=UTF-8'

'''
<form method="POST"
    action="https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/1234567890">

    <input type="hidden" name="cart"
        value="PD94bWwgdmVyc2lvbj0iMS4wIj8+CjxjaGVja291dC1zaG9wcGlu">
    <input type="hidden" name="signature"
        value="kdjsf590GFDGK23l2kgit259fjSDKET0592jalkfwe3539Gjekwu">

    <input type="image" name="Google Checkout" alt="Fast checkout through Google"
        src="http://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=1234567890
              &w=180&h=46&style=white&variant=text&loc=en_US" height="46" width="180">
</form>
'''

production_url = 'https://checkout.google.com/api/checkout/v2/merchantCheckout/Merchant/%s' % merchant_id
sandbox_url = 'https://sandbox.google.com/checkout/api/checkout/v2/merchantCheckout/Merchant/%s' % merchant_id

https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/MERCHANT_ID/diagnose


# create shopping cart request
'''<?xml version="1.0" encoding="UTF-8"?>
<checkout-shopping-cart xmlns="http://checkout.google.com/schema/2">
  <shopping-cart>
    <items>
      <item>
        <item-name>HelloWorld 2GB MP3 Player</item-name>
        <item-description>HelloWorld, the simple MP3 player</item-description>
        <unit-price currency="USD">159.99</unit-price>
        <quantity>1</quantity>
      </item>
    </items>
  </shopping-cart>
  <checkout-flow-support>
    <merchant-checkout-flow-support>
      <shipping-methods>
        <flat-rate-shipping name="SuperShip Ground">
          <price currency="USD">9.99</price>
        </flat-rate-shipping>
      </shipping-methods>
    </merchant-checkout-flow-support>
  </checkout-flow-support>
</checkout-shopping-cart>
'''

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