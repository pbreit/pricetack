# -*- coding: utf-8 -*-

def is_reserved_subdomain(subdomain):
    return subdomain in reserved_subdomains

reserved_subdomains = ['account', 'checkout', 'secure', 'service', 'stores', 'support', 'tickets']