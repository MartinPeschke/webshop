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


dependencies = ['django', 'mysql-python', 'simplejson', 'supervisor', 'PIL']
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
  with cd(environment_path):
    run("env/bin/supervisorctl -c supervisor.cfg stop all", pty=True)
  run("rm -rf {}code/*".format(environment_path))
  run("cp -R {}{}/* {}code/".format(workspace, env, environment_path))
  with cd(environment_path):
    result = run("env/bin/supervisorctl -c supervisor.cfg start all", pty=True)
    if "ERROR" in result:
      run("tail -n50 logs/python.log", pty=True)
      fabric.utils.abort("supervisord did not start: {}".format(result))
  


def build_statics(env):
  environment_path = get_deploy_path(env)
  with cd("{}code/WebShop/per4/media".format(environment_path)):
    if(not files.exists("css")):
      run("mkdir -p css")
    run("~/node_modules/less/bin/lessc less/site.less css/site.css")
    run("java -jar ~/resources/yuicompressor-2.4.7.jar --type css -o css/site.css css/site.min.css")
    run("java -jar ~/resources/compiler.jar --compilation_level WHITESPACE_ONLY --js scripts/libs/bootstrap.min.js scripts/libs/JSON.js scripts/libs/underscore.js scripts/libs/Backbone.js scripts/site.js --js_output_file scripts/build/libs.js")
    run("echo $RANDOM$RANDOM$RANDOM > ./VERSION_TOKEN")
    
def deploy(env):
  clean_local()
  package(env)
  push_package(env)
  unpack_package(env)
  build(env)
  build_statics(env)
  clean_local()  
    