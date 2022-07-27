import time
import datetime
import re

def run_all():
    mail_queue()
    expire_items()
    email_watchlist()
    release_pending_orders()
    update_change_dates()

def mail_queue():
    rows = db(db.mail_queue.status=='pending').select()
    for row in rows:
        try:
            mail.send(to=row.recipient, subject=row.subject, message=row.message, reply_to=row.reply_to)
        except Exception, e:
            row.update_record(status='failed', err_msg=e)
        else:
            row.update_record(status='sent', sent_on=datetime.datetime.now())

def update_change_dates():
    items = db(db.item.change_date < request.now).select()
    for item in items:
        #listing = db(db.listing.item==item.id).select().first()
        listing = None
        if listing:
            from ebay import ebay_call
            auth_service = db((db.auth_service.auth_user==item.created_by) &
                    (db.auth_service.name=='ebay')).select().first()
            data = {'item_id': listing.ref_id, 'price': item.current_price}
            result = ebay_call('ReviseItem', token=auth_service.token, data=data)
            app_logging.info(result)
        item.update_record(change_date=get_change_date(item))

def relist_expired_items():
    items = db(db.item.expire_date < request.now).select()
    for item in items:
        try:
            item.update_record(start_date=item.expire_date, drops=item.drops, duration=item.duration)
            update_watchlist(item.id, 'expired')
        except Exception, e:
            app_logging.info(item)

def email_watchlist():
    time_diff = datetime.timedelta(minutes=30)
    now = request.now + time_diff
    notifications = db((db.watchlist.status=='active') &
            (db.watchlist.send_date<now)).select()
    for notification in notifications:
        try:
            item = db.item(notification.item)
            subject = 'Pricecut on %s' % (item.title,)
            try:
                send_email(queue=True, template='watchlist', recipient=notification.email,
                        subject=subject, context=dict(item=item))
            except Exception, e:
                app_logging.info(e)
            else:
                send_date = item.next_date + datetime.timedelta(days=item.duration)
                if send_date > item.expire_date:
                    notification.update_record(status='inactive')
                elif item.next_date - request.now > time_diff:
                    notification.update_record(send_date=item.next_date)
                else:
                    notification.update_record(send_date=send_date)
        except Exception, e:
            app_logging.info(item)

def release_pending_orders():
    expire_time = request.now - datetime.timedelta(minutes=1)
    purchases = db((db.purchase.status=='pending') &
            (db.purchase.created_on < expire_time) &
            (db.item.id==db.purchase.item)).select()
    for purchase in purchases:
        try:
            purchase.purchase.update_record(status='abandoned')
            purchase.item.update_record(status='active')
        except Exception, e:
            app_logging.info(item)

def google_feed():
    header = ['id','title','link','price','description','condition','image_link']
    feed = open('%s/static/uploads/%s' % (request.folder, 'google_feed.txt'), 'w')
    feed.write('\t'.join(header))
    feed.write('\n')
    items = db(db.item.status=='active')(db.item.grouping!='test').select()
    for item in items:
        try:
            url = 'http://pricetack.com/item/%s' % item.slug
            price = '%s %s' % (item.current_price, item.currency)
            condition = 'used'
            if item.image:
                image_link = 'http://pricetack.com%s' % URL('static','uploads', args=item.image)
            else:
                image_link = ''
            description = html_description(item.description)
            description = '"%s"' % description.replace('"', '""')
            feed.write('\t'.join([str(item.id), item.title, url, price,
                    description, condition, image_link]))
            feed.write('\n')
        except Exception, e:
            app_logging.info(item)
    feed.close()

def bing_feed():
    header = ['MPID','Title','ProductURL','Price','Description','ImageURL']
    feed = open('%s/static/uploads/%s' % (request.folder, 'bingshopping.txt'), 'w')
    feed.write('\t'.join(header))
    feed.write('\r\n')
    items = db(db.item.status=='active')(db.item.grouping!='test').select()
    for item in items:
        if item.currency=='USD':
            try:
                url = 'http://www.pricetack.com/item/%s' % item.slug
                description = re.sub('<[^<]+?>', '', item.description)
                description = '"%s"' % description
                if item.image:
                    image_link = 'http://www.pricetack.com%s' % URL('static','uploads', args=item.image)
                else:
                    image_link = ''
                feed.write('\t'.join([str(item.id), item.title, url,
                        str(item.current_price), description, image_link]))
                feed.write('\r\n')
            except Exception, e:
                app_logging.info(item)
    feed.close()

def oodle_feed():
    header = ['id','title','url','price','currency','description','image_url','country','zip_code']
    feed = open('%sstatic/uploads/%s' % (request.folder, 'oodle_feed.txt'), 'w')
    feed.write('\t'.join(header))
    feed.write('\r\n')
    items = db((db.item.status=='active') &
               (db.item.seller==db.auth_user.id) &
               (db.item.grouping!='test')).select()
    for item in items:
        try:
            url = 'http://www.pricetack.com/item/%s' % item.item.slug
            description = re.sub('<[^<]+?>', '', item.item.description)
            description = '"%s"' % description
            if item.item.image:
                image_link = 'http://www.pricetack.com%s' % URL('static','uploads', args=item.item.image)
            else:
                image_link = ''
            feed.write('\t'.join([str(item.item.id), item.item.title, url,
                    str(item.item.current_price), item.item.currency, description, image_link,
                    item.auth_user.country, item.auth_user.zip]))
            feed.write('\r\n')
        except Exception, e:
                app_logging.info(item)
    feed.close()

def sitemap():
    feed = open('%sstatic/uploads/%s' % (request.folder, 'sitemap.xml'), 'w')
    feed.write('<?xml version="1.0" encoding="UTF-8"?>\r\n')
    feed.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\r\n')
    items = db((db.item.status=='active') &
               (db.item.seller==db.auth_user.id) &
               (db.item.grouping!='test')).select()
    for item in items:
        try:
            feed.write('\t<url>\r\n')
            feed.write('\t\t<loc>http://www.pricetack.com/item/%s</loc>\r\n' % item.item.slug)
            feed.write('\t\t<lastmod>%s</lastmod>\r\n' % item.item.modified_on.strftime('%Y-%m-%d'))
            feed.write('\t\t<changefreq>weekly</changefreq>\r\n')
            feed.write('\t\t<priority>0.9</priority>\r\n')
            feed.write('\t</url>\r\n')
        except Exception, e:
                app_logging.info(item)
    feed.write('</urlset>')
    feed.close()
