# -*- coding: utf-8 -*-
import urllib2
from xml.dom.minidom import Document, parseString
from gluon.html import XML
from lxml import etree
from lxml.builder import E

parser = etree.XMLParser(strip_cdata=False)

config = {'sandbox': {'devid': 'cc232a76-c3c5-4fc4-9740-aee2d9955bc1',
                         'appid': 'Pricetac-3e65-4f4c-b958-c26684c71f02',
                         'certid': '8a45f459-8335-468e-8db3-c15ec149058a',
                         'url': 'https://api.sandbox.ebay.com/ws/api.dll',
                         'runame': 'Pricetack-Pricetac-3e65-4-fbadbkx',
                         'token': 'AgAAAA**AQAAAA**aAAAAA**+I7eTQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4CoAZWHqA2dj6x9nY+seQ**AI8BAA**AAMAAA**PaTJNz36/vrmu4WgyCjGzN/pQ5V/tskFebseQpuGzWoBj4chVrD7vHU4xKQDsXDAX4mkNzWWF+WcKv4GW0kRYGhfotdiNZoGbV3EI/H4duIqWTG5AA8ZfVr78jT1K3BEZEo45VT+HFF+NwsPue25qy4faiDMnyMkotYz03r95bHDoqfAKydJ6vdjWjzEjQnw4i91bZSccHoTVdnyhbSX1t7//no/LBcVhgINiL6Z0kP6r+R84/TvWqlqPN4qVVlTlgigDGvoUs5YXscJ2EId9AIBnbinky8CJp5MwpPL4eQl1jq3Z973xQbGqBLlcWFw5GOAvvLaqX8TUJEaOxP29NxKCzlQ4Zf3Qi6hQD6m8mX1qmBrY527qjIuJ/qDKBDGf3436Q5uHgXtQ1kl7/MDCGBBp6mSx36Yj1Kcm0gAVyTRYPRP3EMqIaSM/hCAxxF6DC2ATC1Ilov/MBOXXd2Ff/mha1jjSiWTgix1Ev7mmVzZBLn0JWcTTL03q6gE38z6Xm17sd/SIuPO4rwk+BxgklHI1hnEVGO1YNBJB2nSZXNwe6rizYvcBq4EziCbqaXQHUMShO36IV7PgGaZ1/WuTPZfW8ICRaV1HzmjXekFmwS20AdMbGrKEVWNXe1gPs3vIhtTQqy0y1TF2HqSrIInoAxW364Ptif2pyCTPObkJozTvK7dz1JMPUa1PMripVomlbBZD9UzWX4Otz9QetcHyokrYdRRBDpa+4XOIucjQjxrRWLoVSRJgfa4aYeLlDcN'},

             'production': {'devid': 'cc232a76-c3c5-4fc4-9740-aee2d9955bc1',
                      'appid': 'Pricetac-c87a-408c-8445-c5ca809a460c',
                      'certid': 'e02535e3-deed-443d-be6e-6906626c9e93',
                      'url': 'https://api.ebay.com/ws/api.dll',
                      'runame': 'Pricetack-Pricetac-c87a-4-qygoqbxce',
                      'token': 'AgAAAA**AQAAAA**aAAAAA**5vrdTQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AEloCiCpCKog+dj6x9nY+seQ**hSkBAA**AAMAAA**UJH0ZrZ0PLhI/OKGPytfUKPSqpPiMvapm3HVQNxrgXeuXXcU91kTatoT9AePhQrVP/7n29xukFqiy8/uqpLm26cuxdbXxw1fPIQ0tiZe/rM5f5FrPYDAlzJ6VVzJ5FYCvpokeuyAinfjH/H2aw3PSWiBxVhAfXp/aIfMU9iyJ7D/Ut4dg98eIDifKhUY8jt0OwFyZlEy+riFM2dof1j8MWG3/anuqh8uK/bjqGmwJDloAHoTZt6+2Xe9n/dRzqxfTEjewvcb41wycalTcT51b9onP/HEsafM8AwDgd1lwSZculb21UvPQWGYa8uApHDsm/rLpMn7Mz25OA+cULq+rjmfDl/fC5j3/MUdl9GKYKhcPOtTTkz1AbZYZfs5LuDejrnSVj8eWFfY+pcnhLaRKzHG4mypuVJEh0VFE96Ii1okb8EdoTM2PbWrdZDP/MRgFRsEULCU1PAkbwPHV488qe7DUzYR2W6cp/5lAwdnUlbevVbt7rbhpv6RqHur26Twcydy9Ys1k10gualnvT20DjShhBZiH01MnEgGO178PiuPwJj7SabM0riqQxEKhaV6dz6sCyXhYXWoD+zP/C431AG/hu8IxsD/TPiGMAqXLWds2thz7JWfQrq1MzySMAyMZySXpeF+8phAyPgsqG9XSKk1eyVSrStqI+ko9HlalO6Q+7d13pIiQaKi11x+QBr2cBO1bqPqVlVwQDOIOQdeeVkq3//vcVFwOyj/Wz+qzW+EZ7D6bLZCwSfu8hsGAGjF'}}

def ebay_headers(config, version, call_name, site_id):
    headers = {'X-EBAY-API-DEV-NAME': config['devid'],
               'X-EBAY-API-APP-NAME': config['appid'],
               'X-EBAY-API-CERT-NAME': config['certid'],
               'X-EBAY-API-COMPATIBILITY-LEVEL': version,
               'X-EBAY-API-CALL-NAME': call_name,
               'X-EBAY-API-SITEID': site_id,
               'Content-Type': 'text/xml'}
    return headers

def GeteBayOfficialTime(token, data={}):
    doc = (
        E.GeteBayOfficialTimeRequest (
            E.RequesterCredentials (E.eBayAuthToken(token)),
            xmlns='urn:ebay:apis:eBLBaseComponents'
        )
    )
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def GetCategories(token, data):
    doc = (
        E.GetCategoriesRequest(
            E.RequesterCredentials (E.eBayAuthToken(token)),
            E.DetailLevel(data.get('DetailLevel', 'ReturnAll')),
            E.LevelLimit(data.get('LevelLimit', '1')),
            E.ViewAllNodes(data.get('ViewAllNodes', 'True')),
            xmlns='urn:ebay:apis:eBLBaseComponents'
        )
    )
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def GetCategorySpecifics(token, data):
    doc = (
        E.GetCategorySpecificsRequest(
            E.RequesterCredentials (E.eBayAuthToken(token)),
            E.CategorySpecificsFileInfo('true'),
            xmlns='urn:ebay:apis:eBLBaseComponents'
        )
    )
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def ReviseItem(token, data):
    if 'title' not in data:
        doc = (
            E.ReviseItemRequest(
                E.RequesterCredentials(E.eBayAuthToken(token)),
                E.WarningLevel(data.get('WarnignLevel', 'High')),
                E.Item(
                    E.ItemID(data['item_id']),
                    E.Currency('USD'),
                    E.StartPrice(str(data['price']), currencyID='USD'),
                ),
                xmlns='urn:ebay:apis:eBLBaseComponents'
            )
        )
    else:
        doc = (
            E.ReviseItemRequest(
                E.RequesterCredentials(E.eBayAuthToken(token)),
                E.WarningLevel(data.get('WarnignLevel', 'High')),
                E.Item(
                    E.ItemID(data['item_id']),
                    E.CategoryMappingAllowed('true'),
                    E.Country('US'),
                    E.Currency('USD'),
                    etree.XML('<Description><![CDATA[%s]]></Description>' % data['description'], parser),
                    E.PictureDetails(E.PictureURL(data.get('image_url', 'http://pricetack.com/static/images/no-photo.png'))),
                    E.ListingDuration('Days_30'),
                    E.ListingType('FixedPriceItem'),
                    E.PostalCode(data.get('zip', '')),
                    E.PaymentMethods(data.get('payment_method', 'PayPal')),
                    E.PayPalEmailAddress(data.get('paypal_email', '')),
                    E.PrimaryCategory (E.CategoryID(data['ebay_category'])),
                    E.Quantity(data['quantity']),
                    E.ConditionID('3000'),
                    E.StartPrice(str(data['price']), currencyID='USD'),
                    E.Title(data['title']),
                    E.ShippingDetails(
                        E.ShippingType('Flat'),
                        E.ShippingServiceOptions(
                            E.ShippingService('USPSFirstClass'),
                            E.ShippingServiceCost(str(data.get('shipping_amount', '0.00')), currencyID='USD'))),
                    E.DispatchTimeMax('3'),
                    E.ReturnPolicy(
                        E.Description('Returns may be accepted for a full or partial refund.'),
                        E.ReturnsAcceptedOption('ReturnsAccepted'))
                ),
                xmlns='urn:ebay:apis:eBLBaseComponents'
            )
        )
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def AddItem(token, data):
    doc = (
        E.AddItemRequest(
            E.RequesterCredentials(E.eBayAuthToken(token)),
            E.WarningLevel(data.get('WarnignLevel', 'High')),
            E.Item(
                E.CategoryMappingAllowed('true'),
                E.Country('US'),
                E.Currency('USD'),
                etree.XML('<Description><![CDATA[%s]]></Description>' % data['description'], parser),
                E.PictureDetails(E.PictureURL(data.get('image_url', 'http://pics.ebay.com/aw/pics/dot_clear.gif'))),
                E.ListingDuration('Days_30'),
                E.ListingType('FixedPriceItem'),
                E.PostalCode(data.get('zip', '94107')),
                E.PaymentMethods(data.get('payment_method', 'PayPal')),
                E.PayPalEmailAddress(data.get('paypal_email', 'paypal@pricetack.com')),
                E.PrimaryCategory(E.CategoryID(data['ebay_category'])),
                E.Quantity(data['quantity']),
                E.ConditionID('3000'),
                E.StartPrice(str(data['price']), currencyID='USD'),
                E.Title(data['title']),
                E.ShippingDetails(
                    E.ShippingType('Flat'),
                    E.ShippingServiceOptions(
                        E.ShippingService('USPSFirstClass'),
                        E.ShippingServiceCost(str(data.get('shipping_amount', '0.00')), currencyID='USD'))),
                E.DispatchTimeMax('3'),
                E.ReturnPolicy(
                    E.Description('Returns may be accepted for a full or partial refund.'),
                    E.ReturnsAcceptedOption('ReturnsAccepted'))),
            xmlns='urn:ebay:apis:eBLBaseComponents'))
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def EndItem(token, data):
    doc = (
        E.EndItemRequest(
            E.RequesterCredentials(E.eBayAuthToken(token)),
            E.ItemID(data['ref_id']),
            E.EndingReason('NotAvailable'),
            xmlns='urn:ebay:apis:eBLBaseComponents'))
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def SetNotificationPreferences(token, data):
    doc = (
        E.SetNotificationPreferencesRequest(
            E.RequesterCredentials(E.eBayAuthToken(token)),
            E.ApplicationDeliveryPreferences(
                E.AlertEmail('mailto://ebay@pricetack.com'),
                E.AlertEnable('Enable'),
                E.ApplicationEnable('Enable'),
                E.ApplicationURL('mailto://ebay@pricetack.com')),
            E.UserDeliveryPreferenceArray(
                E.NotificationEnable(
                    E.EventType('FixedPriceEndOfTransaction'),
                    E.EventEnable('Enable'))),
            xmlns='urn:ebay:apis:eBLBaseComponents'))
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def GetSessionID(token, data):
    runame = config
    doc = (
        E.GetSessionIDRequest(
            E.RequesterCredentials(E.eBayAuthToken(token)),
            E.RuName(data['runame']),
            xmlns='urn:ebay:apis:eBLBaseComponents'))
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def FetchToken(token, data):
    doc = (
        E.FetchTokenRequest(
            E.RequesterCredentials(E.eBayAuthToken(token)),
            E.SessionID(data['session_id']),
            xmlns='urn:ebay:apis:eBLBaseComponents'))
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def RevokeToken(token, data):
    doc = (
        E.RevokeTokenRequest(
            E.RequesterCredentials(E.eBayAuthToken(token)),
            xmlns='urn:ebay:apis:eBLBaseComponents'))
    return etree.tostring(doc, xml_declaration=True, encoding='utf-8')

def ebay_call(call_name, environment='sandbox', token=None, data={}):
    token = token or config[environment]['token']
    data['runame'] = config[environment]['runame']
    func = globals()[call_name]
    xml = func(token, data)
    url = config[environment]['url']
    headers = ebay_headers(config[environment], '723', call_name, '0')
    req = urllib2.Request(url, xml, headers)
    try:
        response = urllib2.urlopen(req)
    except Exception, e:
        return e
    data = response.read()
    root = etree.fromstring(data)
    ebayns = '{urn:ebay:apis:eBLBaseComponents}'
    if root.findtext(ebayns+'Ack')=='Failure':
        if root.findtext(ebayns+'ErrorCode')=='931':
            pass
    return data
