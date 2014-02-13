"""
  easy_install mako
"""
from fabric.api import local
from fabric.api import run, local, run, cd, lcd, put
from fabric.contrib import files

import shutil, os, md5, fabric
from datetime import datetime
from collections import namedtuple
from mako.template import Template
SubSite = namedtuple("SubSite", ["location", "scripts", "styles"])
Style = namedtuple("Style", ["list", "hasBuster"])
Environment=namedtuple("Environment",["repository","process_groups","branch"])

############## CONFIG #########################

PROJECTNAME="webshop"
SUBSITES = [
    SubSite(location = '.', scripts=["libs.js","site.js"], styles=Style(['less/site.less', 'less/welcome.less'], True))
  ]

CLEAN_SESSIONS = False


ENVIRONMENTS = {
    'dev':Environment(
            repository="www-data@aberdeen:/server/git_repositories/webshop_django.git"
            ,process_groups=['p1','p2']
            ,branch='master')
    , 'live':Environment(
            repository="www-data@aberdeen:/server/git_repositories/webshop_django.git"
            ,process_groups=['p1','p2']
            ,branch='master')
}

dependencies = ['django', 'mysql-python', 'simplejson', 'PIL', 'uwsgi']
EXTRA_SETUP = ['./env/bin/pip install -e git+git://github.com/earle/django-bootstrap.git#egg=bootstrap']


############## DONT TOUCH THIS ################

root = '/server/www/{}/'.format(PROJECTNAME)
def get_deploy_path(env):
  return "{}{}/".format(root, env)
def get_code_path(env, version):
    return '{}code/{}/'.format(get_deploy_path(env), version)
def getShortToken(version):
    return md5.new(version).hexdigest()



def create_env(env):
  env_path = get_deploy_path(env)
  if files.exists(env_path):
    with cd(get_deploy_path(env)):
      run("rm -rf *")
      run("mkdir -p {run,logs,code,env,repo.git,static}")
  else:
    run("mkdir -p {}/{{run,logs,code,env,repo.git,static}}".format(env_path))

  with cd(get_deploy_path(env)):
    run("virtualenv --no-site-packages env")
    run("env/bin/easy_install supervisor")
  
  cfg_template = Template(filename='supervisor.cfg.mako')

  with cd(env_path):
    if files.exists("supervisor.cfg"): 
      run("rm supervisor.cfg")
    files.append("supervisor.cfg", cfg_template.render(env = env), escape=False)
    run("env/bin/supervisord -c supervisor.cfg")
    with cd("repo.git"):
      run("git clone {} .".format(ENVIRONMENTS[env].repository))
      run("git checkout {}".format(ENVIRONMENTS[env].branch))
    for dep in dependencies:
      run("./env/bin/easy_install {}".format(dep))
    for extra in EXTRA_SETUP:
      run(extra)


def update(env):
  with cd("{}repo.git".format(get_deploy_path(env))):
    run("git pull")

def build(env, version):
  environment_path = get_deploy_path(env)
  code_path = get_code_path(env, version)

  run("mkdir {}".format(code_path))
  with cd(code_path):
    run("cp -R {}repo.git/webapp/* .".format(environment_path))

def build_statics(env, version):
    code_path = get_code_path(env, version)
  
    # build player skin
    with cd(code_path):
        for subsite in SUBSITES:
            loc = subsite.location
            def getPath(path):
                return "{project}/{subsite}/static/{path}".format(project=PROJECTNAME, subsite=loc, path=path)

            style = subsite.styles
            if not files.exists(getPath("css")):
                run("mkdir -p {}".format(getPath("css")))

            if style.hasBuster:
                files.sed(getPath("less/cachebuster.less"), "CACHEBUSTTOKEN", '"{}"'.format(getShortToken(version)))

            for stylesheet in style.list:
                fname = stylesheet.rsplit(".")[0].split('/')[-1]
                run("~/node_modules/less/bin/lessc {project}/{subsite}/static/{stylesheet} --clean-css {project}/{subsite}/static/css/{outname}.min.css".format(project=PROJECTNAME, subsite=loc, stylesheet=stylesheet, outname = fname))



        for subsite in SUBSITES:
            if subsite.scripts:
                if not files.exists("{project}/{subsite}/static/scripts/build/".format(project=PROJECTNAME, subsite=subsite.location)):
                    run("mkdir -p {project}/{subsite}/static/scripts/build/".format(project=PROJECTNAME, subsite=subsite.location))

                customs = " ".join(["{project}/{subsite}/static/scripts/{script}".format(project=PROJECTNAME, subsite=subsite.location, script = script) for script in subsite.scripts])
                run("java -jar ~/resources/compiler.jar --compilation_level SIMPLE_OPTIMIZATIONS \
                    --js {customs} \
                    --warning_level QUIET --js_output_file {project}/{subsite}/static/scripts/build/site.js".format(project=PROJECTNAME, subsite=subsite.location, customs = customs))
        run("echo {} > ./VERSION_TOKEN".format(getShortToken(version)))



def switch(env, version):
    environment_path = get_deploy_path(env)
    with cd(environment_path):
        with cd("code"):
            run("rm current;ln -s {} current".format(version))
        for pg in ENVIRONMENTS[env].process_groups:
            result = run("env/bin/supervisorctl -c supervisor.cfg restart {}:*".format(pg), pty=True)
            if "ERROR" in result:
              run("tail -n50 logs/python*.log", pty=True)
              fabric.utils.abort("Process group did not start:{}: {}".format(pg, result))


def deploy(env):
  VERSION_TOKEN = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
  update(env)
  build(env, VERSION_TOKEN)
  build_statics(env, VERSION_TOKEN)
  switch(env, VERSION_TOKEN)