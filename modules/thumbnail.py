# -*- coding: utf-8 -*-

# http://www.web2pyslices.com/main/slices/take_slice/62
# http://www.pythonware.com/library/pil/handbook/introduction.htm
def makeThumbnail(img_name,size=(150,150)):
    try:    
        import os
        from PIL import Image
    except: 
        return
    im=Image.open(request.folder + 'uploads/' + img_name)
    im.thumbnail(size,Image.ANTIALIAS)
    root,ext = os.path.splitext(img_name)
    thumbName='%s_thumb%s' %(root, ext)
    im.save(request.folder + 'uploads/' + thumbName)
    return thumbName

def add():
    form = SQLFORM(db.Item)
    if form.accepts(request, session):
        response.flash = "Item Added"
        row = db(db.Item.id==form.vars.id).select()[0]
        img_name=row.image
        thumb = makeThumbnail(img_name)
        if thumb: row.update_record(image_thumb=thumb)
    elif form.errors:
        response.flash = "Form has errors"
    return dict(form=form)

# https://groups.google.com/forum/#!searchin/web2py/pil/web2py/xIRj225Ovyw/1jh-gTh-XygJ
def __call__(self, value): 

        import Image 
        import cgi 

        try: 
                im = Image.open(value.file) 
                print im.size, im.format 

                im.thumbnail((100, 100), Image.ANTIALIAS) 

                value.file.seek(0) 
                im.save(value.file, im.format) 
                value.file.seek(0) 

                return (value, None) 
        except Exception as e: 
                print 'resize exception:', e 
                return (value, self.error_message)
