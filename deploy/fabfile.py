"""
  easy_install mako
"""
from fabric.api import local
from fabric.api import run, local, run, cd, lcd, put
from fabric.contrib import files

import shutil, os, md5, datetime, fabric
from mako.template import Template
from tempfile import NamedTemporaryFile

root = '/server/www/'
workspace = '{}workspace/'.format(root)
deploy_space = '{}deployment/'.format(root)
transport_name = "deploypackage"

statics_source = root
statics_destination = 'WebShop/per4/media'


dependencies = ['django', 'mysql-python']
extra_dependencies = ['pip install -e git+git://github.com/earle/django-bootstrap.git#egg=bootstrap']




def get_deploy_path(env):
  return "{}{}/".format(deploy_space, env)
def get_full_transport_name(env):
  return "{}.{}.tar.bz2".format(transport_name, env)
def get_full_statics_destination(env):
  return "{}{}/code/{}".format(deploy_space, env, statics_destination)
  
  
  
def clean_local():
  if(os.path.exists('tmp')):
    shutil.rmtree("tmp")

def clean_remote(env):
  environment_path = get_deploy_path(env)
  with cd(environment_path):
    run("rm -rf env/*")
    run("virtualenv --no-site-packages env")
    for package in dependencies:
      run("env/bin/easy_install {}".format(package))
    for command in extra_dependencies:
      run("env/bin/{}".format(command))

def create_env(env):
  environment_path = get_deploy_path(env)
  with cd(deploy_space):
    run("rm -rf {}".format(env))
    run("mkdir -p %s/{run,logs,code,env}" % env)
  clean_remote(env)


def package(env):
  clean_local()
  os.mkdir("tmp")
  shutil.make_archive("tmp/deploypackage.{}".format(env), "bztar", "../webshop")

def push_package(env):
    with cd(workspace):
      with lcd('tmp'):
        run("rm -rf *")
        put(get_full_transport_name(env), get_full_transport_name(env))

def unpack_package(env):
  with cd(workspace):
    run("rm -rf {}".format(env))
    run("mkdir {}".format(env))
    run("tar xfvj {} -C {}".format(get_full_transport_name(env), env))

def build(env):
  environment_path = get_deploy_path(env)
  run("rm -rf {}code/*".format(environment_path))
  run("cp -R {}{}/* {}code/".format(workspace, env, environment_path))
  with cd(get_full_statics_destination()):
    run("ln -s {}files files".format(statics_source))
    run("ln -s {}downloads downloads".format(statics_source))
  


def build_statics(env):
  environment_path = get_deploy_path(env)
  with cd("{}code/webshop/static".format(environment_path)):
    run("ln -s /server/www/files/ p")
    #if(not files.exists("giftcannon/website/static/css")):
    #  run("mkdir -p giftcannon/website/static/css")
    #result = run("~/node_modules/less/bin/lessc giftcannon/website/static/less/main.less giftcannon/website/static/css/step1.css")
    #run("cat giftcannon/website/static/less/normalize.css giftcannon/website/static/less/transitions.css giftcannon/website/static/css/step1.css > giftcannon/website/static/css/step2.css")
    #run("java -jar resources/yuicompressor-2.4.7.jar --type css -o giftcannon/website/static/css/site.css giftcannon/website/static/css/step2.css")
    #run("rm giftcannon/website/static/css/step*.css")
    #run("java -jar resources/compiler.jar --compilation_level WHITESPACE_ONLY --js giftcannon/website/static/scripts/libs/JSON.js giftcannon/website/static/scripts/libs/underscore.js giftcannon/website/static/scripts/libs/sprints8.js giftcannon/website/static/scripts/libs/FBHandler.js giftcannon/website/static/scripts/libs/Backbone.js --js_output_file giftcannon/website/static/scripts/build/libs.js")
    #run("echo $RANDOM$RANDOM$RANDOM > ./VERSION_TOKEN")
    
def deploy(env):
  clean_local()
  package(env)
  push_package(env)
  unpack_package(env)
  build(env)
  #build_statics(env)
  clean_local()  
    