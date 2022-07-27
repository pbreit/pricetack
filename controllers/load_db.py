# -*- coding: utf-8 -*-

pw, error_message = CRYPT(auth.settings.hmac_key)('111111') 
auth_users = [{'email': 'pb@pricetack.com', 'password': pw, 'name': 'pbreit', 'paypal_email': 'pb@pricetack.com'}]
auth_groups = [{'role': 'impersonators'}]
auth_memberships = [{'user_id': 1, 'group_id': 1}]
auth_permissions = [{'group_id': 1, 'name': 'impersonate', 'table_name': 'auth_user'}]
items = [{'title': 'Item 100', 'seller': 1, 'start_price': '10.00', 'drops': 4, 'duration': 3, 'price_change': 1.0, 'grouping': 'Group1', 'created_by': 1, 'modified_by': 1},
    {'title': 'Item 200', 'seller': 1, 'start_price': '100.00', 'drops': 4, 'duration': 10, 'price_change': 10.0, 'grouping': 'Group2', 'created_by': 1, 'modified_by': 1}]

def index():
    db.auth_user.bulk_insert(auth_users)
    db.auth_group.bulk_insert(auth_groups)
    db.auth_membership.bulk_insert(auth_memberships)
    db.auth_permission.bulk_insert(auth_permissions)
    db.item.bulk_insert(items)
    return dict()
