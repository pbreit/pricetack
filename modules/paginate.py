# -*- coding: utf-8 -*-
from gluon.html import A, URL
from gluon.cache import Cache

class Pagination():
    def __init__(self, db, query, 
                 orderby, current=None, 
                 display_count=4, cache=None,
                 r=None, res=None):
        self.db = db
        self.query = query
        self.orderby = orderby
        if not current:
            if not r.vars.p:
                current = 0
            else:
                current = int(r.vars.p)
        elif not isinstance(current, int):
            current = int(current)
        self.current = current
        self.display_count = display_count
        self.r = r
        self.res = res
        if not cache:
            self.cache = (Cache(r).ram, 1500)
        else:
            self.cache = cache
        
    def get_set(self, set_links = True):
        self.set = self.db(self.query).select(
            orderby=self.orderby, limitby=(
                self.current, self.current+self.display_count
                ), cache=self.cache
            )
        self.num_results = len(self.set)
        self.total_results = self.db(self.query).count()
        if set_links:
            self.res.paginate_links = self.generate_links()
            
        return self.set
    
    def generate_links(self):
        self.backward = A('<< previous', _href=URL(r=self.r, args=self.r.args, vars={'p': self.current - self.display_count})) if self.current else ''
        self.forward = A('next >>', _href=URL(r=self.r, args=self.r.args, vars={'p': self.current + self.display_count})) if self.total_results > self.current + self.display_count else ''
        self.location = 'Showing %d to %d out of %d records' % (self.current + 1, self.current + self.num_results, self.total_results)
        return (self.backward, self.forward, self.location)

class Paginator(DIV):
     items_per_page = 10
     records = 100

    def limitby(self):
        from gluon import current
        page = self.page = int(current.request.vars.page or 0)
        return (self.items_per_page*page, self.items_per_page*(page+1))

    def xml(self):
        from gluon import current
        pages, rem = divmod(self.records, self.items_per_page)
        if rem: pages += 1
        if self.page > 0:
            self.append(A('first', _href=URL(args=current.request.args, vars=dict(page=0))))
        if self.page > 1:
            self.append(A('prev', _href=URL(args=current.request.args, vars=dict(page=self.page-1))))
        if self.page < pages-2:
            self.append(A('next', _href=URL(args=current.request.args, vars=dict(page=self.page+1))))
        if self.page < pages-1:
            self.append(A('last', _href=URL(args=current.request.args, vars=dict(page=pages-1))))
        return DIV.xml(self)

def index():
    p = Paginator()
    p.items_per_page = 5
    p.records = db(query).count()
    rows = db(query).select(limitby=p.limitby())
    return dict(rows=rows, paginator=p)

{{extend 'layout.html'}}
{{=SQLTABLE(rows)}}
{{=paginator}} 