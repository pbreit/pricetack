# -*- coding: utf-8 -*-
import cPickle

@auth.requires_membership('impersonators')
def index():
    users = {}
    email = request.vars.email or None
    form = SQLFORM.factory(Field('email'))
    if form.accepts(request, session):
        users = db(db.auth_user.email.contains(email)).select()
    return dict(form=form, users=users)

@auth.requires_membership('impersonators')
def impersonate():
    user_id = request.vars.user_id or None
    current_id = auth.user.id
    if user_id and user_id != auth.user.id and user_id != '0':
        user = db.auth_user(user_id)
        if not user:
            raise HTTP(401, "Not Found")
        auth.impersonator = cPickle.dumps(session)
        auth.user.update(db.auth_user._filter_fields(user, True))
        user = auth.user
        if auth.settings.login_onaccept:
            form = Storage(dict(vars=auth.user))
            auth.settings.login_onaccept(form)
        log = auth.messages.impersonate_log
        if log:
            auth.log_event(log % dict(id=current_id, other_id=auth.user.id))
        session.flash = 'logged in as %s' % auth.user.email
        redirect(URL('manage', 'index'))
    elif user_id in (0, '0') and auth.is_impersonating():
        session.clear()
        session.update(cPickle.loads(auth.impersonator))
        auth.user = session.auth.user

@auth.requires_login()
def index():
    return dict()

@auth.requires_login()
def export_db():
    db.export_to_csv_file(open('/root/export.csv', 'wb'))

@auth.requires_login()
def import_db():
    db.import_from_csv_file(open('/root/export.csv', 'rb'))

@auth.requires_login()
def migrate():
    items = db(db.item.id>0).select()
    for item in items:
        item.update_record(views=0, modified_on=item.modified_on, modified_by=item.modified_by)
    return len(items)

def test_email():
    try:
        result = mail.send(to='pbreitenbach@mac.com', subject='Subject', message='Message.', reply_to='service@pricetack.com')
    except Exception, e:
        return dict(e=e, result=result)
    return dict(e='Success', result=result)

def test_queue():
    db.mail_queue.insert(
            status='pending',
            recipient='pbreitenbach@gmail.com',
            sender='service@pricetack.com',
            reply_to='service@pricetack.com',
            subject='Subject',
            message='Message')
