# -*- coding: utf-8 -*- 

extractor = local_import('extractor')

def index():
    return extractor.extract(settings, db)
