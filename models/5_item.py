# -*- coding: utf-8 -*-
import os.path
from PIL import Image
from decimal import *

def get_change_date(self):
    start_date = (self.start_date if 'start_date' in self else request.now)
    periods = ((request.now - start_date).days / self.duration) + 1
    change_date = start_date + datetime.timedelta(days=(periods * self.duration))
    return change_date

def get_expire_date(self):
    start_date = (self.start_date if 'start_date' in self else request.now)
    expire_date = start_date + datetime.timedelta(days=((self.drops + 1) * (self.duration)))
    return expire_date

db.define_table('item',
    Field('title', length=128),
    Field('seller', 'integer', default=auth.user_id, readable=False, writable=False),
    Field('status', default='active', readable=False, writable=False),
    Field('description', 'text', default=''),
    Field('quantity', 'integer', default=1),
    Field('grouping', default=''),
    Field('category', 'integer', readable=False, writable=False),
    Field('condition', readable=False, writable=False),
    Field('image', 'upload', uploadfolder=request.folder+'static/uploads',
            requires=IS_EMPTY_OR(IS_IMAGE())),
    Field('image_display', 'upload', uploadfolder=request.folder+'static/uploads',
            readable=False, writable=False),
    Field('image_thumb', 'upload', uploadfolder=request.folder+'static/uploads',
            readable=False, writable=False),
    Field('image_url'),
    Field('currency', default='USD'),
    Field('is_local', 'boolean', default=False),
    Field('shipping_method', 'integer', default=1),
    Field('shipping_amount', 'decimal(17,2)', default=0.0),
    Field('tax_state'),
    Field('tax_rate', 'decimal(5,2)', default=0.0),
    Field('start_price', 'decimal(17,2)'),
    Field('drops', 'integer', default=4),
    Field('duration', 'integer', default=7),
    Field('price_change', 'decimal(17,2)'),
    Field('start_date', 'datetime', default=request.now, readable=False, writable=False),
    Field('change_date', 'datetime'),
    Field('expire_date', 'datetime'),
    Field('views', 'integer', default=0, readable=False, writable=False),
    Field('auto_relist', 'boolean', default=True),
    Field('hide_schedule', 'boolean', default=False),
    #Field('show_schedule', 'boolean', default=False),
    Field('hide_quantity', 'boolean', default=False),
    #Field('show_quantity', 'boolean', default=True),
    Field('flags', 'list:string', readable=False, writable=False),
    record_signature)

db.item.change_date.compute = lambda r: get_change_date(r)
db.item.expire_date.compute = lambda r: get_expire_date(r)

db.item.image_thumb.compute = lambda r: resize_image(r['image'], (150,130), 'thumb')
db.item.image_display.compute = lambda r: resize_image(r['image'], (320,320), 'display')

db.item.status.requires = IS_IN_SET(['inactive','active','pending','sold','shipped','canceled','expired'])
#db.item.condition.requires = IS_IN_SET(['New','Like New','Preowned'], zero=T('choose one'))
db.item.drops.requires = IS_IN_SET([1,2,3,4,5,6], zero=None)
db.item.duration.requires = IS_IN_SET([1,2,3,5,7,10,14,21,28,30], zero=None)
db.item.currency.requires = IS_IN_SET(['USD','AUD','CAD','EUR','GBP','MXN'], zero=None)
db.item.start_price.requires = [IS_NOT_EMPTY(), IS_DECIMAL_IN_RANGE(0.01, 99999.99)]
db.item.price_change.requires = [IS_NOT_EMPTY(), IS_DECIMAL_IN_RANGE(0.01, 99999.99)]
db.item.shipping_amount.requires = [IS_NOT_EMPTY(), IS_DECIMAL_IN_RANGE(0.00, 99999.99)]

#item virtual fields
class ItemVirtualPrices(object):

    def prices(self):
        p = []
        for i in range(0, self.item.drops + 1):
            d = self.item.start_date + datetime.timedelta(days=(i * self.item.duration))
            amt = self.item.start_price - (i * self.item.price_change)
            if amt < 0.01:
                amt = Decimal('0.01')
            p.append({'raw_date': d, 'short_date': d.strftime('%b %d'), 'long_date': d.strftime('%b %d %H:%M %p PT'), 'amt': amt})
        return p

db.item.virtualfields.append(ItemVirtualPrices())

class ItemVirtualFields(object):

    def current_period(self):
        if (request.now - self.item.start_date).days >= ((self.item.drops + 1) * self.item.duration):
            return self.item.drops
        else:
            return int((request.now - self.item.start_date).days / self.item.duration)

    def current_price(self):
        return self.item.prices[self.item.current_period]['amt']

    def next_date(self):
        if self.item.current_period+1==len(self.item.prices):
            return self.item.expire_date - datetime.timedelta(minutes=30)
        else:
            return self.item.prices[self.item.current_period+1]['raw_date'] - datetime.timedelta(minutes=30)

    def last_price(self):
        return self.item.prices[-1]['amt']

    def last_date(self):
        return self.item.prices[-1]['short_date']

    def currency_symbol(self):
        if self.item.currency in ['USD', 'AUD', 'CAD', 'MXN']:
            return '$'
        elif self.item.currency=='GBP':
            return '£'
        elif self.item.currency=='EUR':
            return '€'
        else:
            return ''

    def shipping_method_name(self):
        return (shipping_methods[self.item.shipping_method])

    def slug(self):
        return '%s-%s' % (slugify(self.item.title, maxlen=50), self.item.id)

def html_description(description):
    if description.find('</')>-1:
        return description
    else:
        return str(MARKMIN(description))

db.item.virtualfields.append(ItemVirtualFields())

def slugify(value, maxlen=80):
    return IS_SLUG(maxlen=maxlen)(value)[0]

def id_from_slug(slug):
    if slug:
        item_id = str(slug).split('-')[-1]
        if item_id.isdigit():
            return int(item_id)
    return None

def resize_image(image, size, path, rotate=0):
    if image:
        try:
            img = Image.open('%sstatic/uploads/%s' % (request.folder, image))
            img = img.convert("RGB")
            img.thumbnail(size, Image.ANTIALIAS)
            img = img.rotate(rotate)
            root, ext = os.path.splitext(image)
            filename = '%s_%s%s' %(root, path, ext)
            img.save('%sstatic/uploads/%s' % (request.folder, filename))
            return filename
        except Exception as e:
            return e
    else:
        return None

shipping_methods = {
    1: 'see description',
    100: 'USPS First Class (US)',
    105: 'USPS Priority (US)',
    120: 'UPS Ground (US)',
    150: 'Canada Post Regular (CA)',
    155: 'Canada Post Expedited (CA)',
    200: 'Royal Mail 1st (UK)',
    202: 'Royal Mail 2nd (UK)',
    210: 'ParcelForce express48 (UK)',
    600: 'Parcel Post (AU)',
    602: 'Registered Parcel Post (AU)',
    620: 'ParcelPost (NZ)',
    622: 'ParcelPost Tracked (NZ)',
    999: 'See Description'
}

settings.xml_permitted_tags = ['a', 'b', 'blockquote', 'br/', 'div', 'i', 'li', 'meta', 'ol', 'span', 'strong', 'u', 'ul', 'p', 'code', 'pre', 'img/', 'table', 'tbody', 'th', 'tr', 'td']

settings.html_tags = ['!--...--', '!doctype', 'a', 'abbr', 'acronym', 'address', 'applet', 'area', 'b', 'base', 'basefont', 'bdo', 'big', 'blockquote', 'body', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset', 'font', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'isindex', 'kbd', 'label', 'legend', 'li', 'link', 'map', 'menu', 'meta', 'noframes', 'noscript', 'object', 'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 's', 'samp', 'script', 'select', 'small', 'span', 'strike', 'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'u', 'ul', 'var']
