from django.contrib.auth.decorators import user_passes_test
from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings 

import Image, shutil

ROOT_FOLDER = os.path.join(settings.MEDIA_ROOT, 'ads')
IMPORT_FOLDER = os.path.join(ROOT_FOLDER, 'import')
THUMBS_FOLDER = os.path.join(ROOT_FOLDER, 'thumbs')
IMAGE_FOLDER = os.path.join(ROOT_FOLDER)

def move_images(filelist):
    for fname in filelist:
        shutil.move(os.path.join(IMPORT_FOLDER, fname), os.path.join(IMAGE_FOLDER, fname))
    return 1

def create_thumbs(filelist):
    for fname in filelist:
        im = Image.open(os.path.join(IMPORT_FOLDER, fname))
        if(im.mode == "P"): im = im.convert("RGB")

        im.thumbnail((100, 100))
        im.save(os.path.join(THUMBS_FOLDER, fname), 'JPEG')
    return 1

@user_passes_test(lambda u: (not u.is_anonymous()) and u.is_superuser, login_url='/admin/')
def importads(request):
    import_root = IMPORT_FOLDER
    images_to_import = set(os.listdir(IMPORT_FOLDER))
    images_name_collisions = images_to_import & set(os.listdir(IMAGE_FOLDER)) & set(os.listdir(THUMBS_FOLDER))
    images_no_collisions  = set(images_to_import) - images_name_collisions
    
    if(request.GET.get('import',None) == '1'):
        create_thumbs(images_to_import)
        move_images(images_to_import)



    return render_to_response('adsimport.html', locals(), context_instance=RequestContext(request))

