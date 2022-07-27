# -*- coding: utf-8 -*- 
import re

class CLEAN():

    def __init__(self, regex='[\t]'):
        self.regex = re.compile(regex)

    def __call__(self, value):
        v = self.regex.sub('',str(value).strip())
        return (v, None)
