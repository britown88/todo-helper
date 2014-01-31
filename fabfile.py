import json
import os
from fabric.api import *
from fabric.contrib import files
from fabric.utils import abort, error
from jinja2 import Environment, FileSystemLoader
from StringIO import StringIO

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

APP_ENV = json.load(open(os.path.join(PROJECT_PATH, 'config','fabric.json'), 'r'))

##########################################
# Connection Tasks
##########################################

@task
def vagrant(app='all', boot=True, destroy=False):
    if destroy: local('vagrant destroy')
    if boot: local('vagrant up --provider virtualbox')

    env.update(APP_ENV['vagrant'])

    # # use vagrant ssh key
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)

    print result
    env.key_filename = result.split()[1].strip('"')

@task
def melvintest(app='all'):
    env.update(APP_ENV['melvintest'])


@task
def prod():
    pass

##########################################
# Build tasks
# Build installs system dependencies for the projects.
##########################################

@task
def build():
    sudo('sudo add-apt-repository ppa:rwky/redis', pty=False, quiet=True)
    system_update()
    system_install('redis-server')
    system_install('git')
    system_install('nginx uwsgi')

    system_install('python-software-properties python g++ make python-pip python-dev') #pip deps

    sudopip(['virtualenv'])

def pip_install_from_requirements_file():
    run('pip install -r pip-reqs', shell=False)

def sudopip(packages):
    sudo('sudo pip install %s' % ' '.join(packages), shell=False)

def pip(packages):
    run('pip install %s' % ' '.join(packages), shell=False)

def system_update():
    sudo('apt-get -yqq update')

def system_install(*packages):
    sudo('apt-get -yqq install %s' % ' '.join(packages), shell=False)

def render_template_file(filename, nginxVars):
    jinja_env = Environment(loader=FileSystemLoader('templates'))
    tmpl = jinja_env.get_template(filename)
    return StringIO(tmpl.render(nginxVars))


##########################################
# Clonecode/deploy task, and it's related subtasks
##########################################

@task
def deploy():
    put('./config/todo-helper_deploy_key', '~/.ssh/id_rsa', use_sudo=True)

    if files.exists('~/app/todo-helper'):
        with cd('~/app/todo-helper'):
            run('git checkout master')
            run('git pull origin master')
    else:

        sudo('sudo rm -rf ~/app/todo-helper')
        run('mkdir -p ~/app')

        run('git clone https://github.com/p4r4digm/todo-helper.git ~/app/todo-helper',
            pty=False)
        # run('sudo chgrp -R %s ~/app')
        run('sudo chmod -R g+wx ~/app')

    with cd('~/app/todo-helper'):
        run('virtualenv env --no-site-packages')
        # with run('source ./env/bin/activate'):
        with prefix('source ./env/bin/activate'):
            pip_install_from_requirements_file()


@task
def config():
    put('./config/userpass.config', '~/app/todo-helper/config/userpass.config', use_sudo=True)
    put('./webapp/flaskapp/access_token.txt', '~/app/todo-helper/webapp/flaskapp/access_token.txt', use_sudo=True)



##############################################
# restart_all task, and it's related subtasks
# Restart nginx
# restart circus or python
##############################################

@task
def restart_all():
    restart_nginx()
    with cd('~/app/todo-helper/src'):
        run('python todoMelvin.py')

@task
def restart_nginx():
    stop_nginx()
    start_nginx()

@task
def start_nginx():
    sudo('service nginx start')

@task
def stop_nginx():
    sudo('service nginx stop')



##############################################
# MISCELLANEOUS
##############################################

@task
def stop_apache2():
    sudo('service apache2 stop')

# just a test command to see what the OS name is
@task
def uname():
    run('uname -a')
