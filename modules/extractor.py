# -*- coding: utf-8 -*-
import datetime
import gluon.contrib.simplejson as json
import poplib
from optparse import OptionParser
from email import message_from_string
from email.header import decode_header
from email.utils import collapse_rfc2231_value
from StringIO import StringIO


def extract(settings, db):
    """ Main function (extractor) """
    reader = GmailPOPReader(settings)
    message_parser = MessageParser(settings)
    image_saver = ImageSaver(settings, db)
    ret = []
    for raw_message in reader.get_messages():
        try:
            message = message_parser.get_parsed_message(raw_message)
            image_saver.save_message(message)
        except Exception, e:
            ret.append('An exception occured while processing images: %s' % str(e))
    return '\n'.join(ret)



def header_to_unicode(header, default_enc='utf-8', placeholder=u'_'):
    """ Useful utility function. Return decoded header doing all its best to
    decode data to unicode string
    """
    if not header:
        return None
    header_parts = decode_header(header)
    uparts = []
    for val, enc in header_parts:
        if not enc:
            enc = default_enc
        try:
            uval = val.decode(enc)
        except (UnicodeDecodeError, LookupError), e:
            uval = placeholder * len(val)
        uparts.append(uval)
    if uparts and uparts[0]:
        uheader =  u''.join(uparts)
        return uheader
    return None


def guess_filename(raw_part, failobj=None):
    """
    Based on Message.get_filename code function to "guess" filename.

    The issue is that email.Message can save the name of the attachment
    either in Content-Disposition or Content-Type field.

    Filename is always a unicode object
    """
    field_names = 'content-disposition content-type'.split()
    param_names = 'filename name'.split()
    missing = object()
    for field in field_names:
        for param in param_names:
            filename = raw_part.get_param(param, missing, field)
            if not filename is missing:
                value = collapse_rfc2231_value(filename).strip()
                # Some MUA don't bother to encode non-ascii attachments, we
                # should do it by ourselves
                if isinstance(value, str):
                    value = value.decode('utf-8', 'ignore')
                return value
    return failobj


class GmailPOPReader(object):

    def __init__(self, settings):
        self.host = 'pop.gmail.com'
        self.port = 995
        self.username = settings['username']
        self.password = settings['password']
        self.debug = settings['pop3_debug']

    def get_messages(self):
        """ yield raw messages
        @return iterator of strings
        """
        pop = poplib.POP3_SSL(self.host, self.port)
        if self.debug:
            pop.set_debuglevel(1)
        pop.getwelcome()
        pop.user(self.username)
        pop.pass_(self.password)
        _, message_data, _ = pop.list()
        for item in message_data:
            num, size = item.split()
            _, lines, _ = pop.retr(num)
            yield '\n'.join(lines)
        if not self.debug:
            pop.quit()

class MessageParser(object):

    def __init__(self, settings):
        pass

    def get_parsed_message(self, data):
        """ return the parsed message object """
        return ParsedMessage(data)


class ParsedMessage(object):
    """
    Convenient wrapper around email.Message. Has sender and message_id fields
    and get_images() method.
    """

    def __init__(self, data):
        self.message = message_from_string(data)
        self.sender = header_to_unicode(self.message['From'])
        self.message_id = header_to_unicode(self.message['Message-Id'])

    def get_images(self):
        """ yield image attachment as tuple having two
        elements: (filename, contents)
        """
        if self.message.is_multipart():
            for part in self.message.walk():
                if part.get_content_maintype() == 'image':
                    yield self._handle_message_part(part)
        elif self.message.get_content_maintype() == 'image':
            yield self._handle_message_part(self.message)

    def _handle_message_part(self, part):
        default_filename = u'noname.%s' %  part.get_content_subtype() or 'dat'
        filename = guess_filename(part, default_filename)
        return (filename, part.get_payload(decode=True),)


class ImageSaver(object):
    """ Store images in database using web2py DAL """

    def __init__(self, settings, db):
        self.db = db

    def save_message(self, message):
        for filename, image_data in message.get_images():
            stream = StringIO(image_data)
            message_id = self.db.image.insert(
                message_id=message.message_id,
                email=message.sender,
                file=self.db.image.file.store(stream, filename),
            )
            self.db.commit()
