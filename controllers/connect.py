# -*- coding: utf-8 -*-
import urlparse
import oauth2 as oauth
import urllib
import cgi

@auth.requires_login()
def facebook():
    app_id = '215212101842488'
    consumer_key = '35a720def9be69fc3dce887a9d5042f3'
    consumer_secret = '31d5669250d79619f0ff20f128ff607e'
    request_token_url = 'https://graph.facebook.com/oauth/access_token'
    access_token_url = ''
    authorize_url = 'https://www.facebook.com/dialog/oauth'
    return_url = 'http://http://pb-dev.pricetack.com:8001/connect/facebook/return'
    
    if request.args(0)=='authorize':
        scope = 'email,read_stream'
        redirect('%s?client_id=%s&redirect_uri=%s&scope=%s' % (authorize_url, app_id, return_url, scope))
    elif request.args(0)=='return':
        data = {'client_id': app_id,
                'redirect_uri': return_url,
                'client_secret': consumer_secret,
                'code': request.vars.code}
        result = cgi.parse_qs(urllib.urlopen(request_token_url, urllib.urlencode(data)).read())
        if result['error'][0]:
            error_reason, error_description
        else:
            code = result['code'][0]
        
        #client_id=YOUR_APP_ID&redirect_uri=YOUR_URL&client_secret=YOUR_APP_SECRET&code=THE_CODE_FROM_ABOVE
        
        access_token=''
    else:
        return dict()

@auth.requires_login()
def ebay():
    if request.args(0)=='authorize':
        
    else:
        return dict()
    pass

@auth.requires_login()
def paypal():
    pass

@auth.requires_login()
def twitter():
    consumer_key = 'raanoz6TkQmlPdUNxWm31Q'
    consumer_secret = 'mD3kyhsqCyjWSoF6RfO545yVpoFtKGfoPkcmW9seXxQ'
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url = 'http://twitter.com/oauth/access_token'
    authorize_url = 'http://twitter.com/oauth/authorize'

    if request.args(0)=='authorize':
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)
        resp, content = client.request(request_token_url, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(urlparse.parse_qsl(content))
        session.oauth_token = request_token['oauth_token']
        session.oauth_token_secret = request_token['oauth_token_secret']
        redirect('%s?oauth_token=%s' % (authorize_url, request_token['oauth_token']))

    elif request.args(0)=='return':
        token = oauth.Token(session.oauth_token, session.oauth_token_secret)
        token.set_verifier(request.vars.oauth_verifier)
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer, token)
        resp, content = client.request(access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        db.auth_service.insert(
                user=auth.user.id,
                name='twitter',
                uname=access_token['screen_name'],
                uid=access_token['user_id'],
                token='%s|%s' % (access_token['oauth_token'], access_token['oauth_token_secret']))
        return dict(screen_name=access_token['screen_name'])
    else:
        return dict()
