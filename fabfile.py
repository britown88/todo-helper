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

    env.hosts = ['127.0.0.1:2275']

    # env.update(APP_ENV['vagrant'])

    # # use vagrant ssh key
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)

    print result
    env.key_filename = result.split()[1].strip('"')
    env.user = 'vagrant'
    env.disable_known_hosts = True

@task
def melvintest(app='all'):
    env.hosts = ['23.22.5.73']

    env.key_filename = '~/.amazonkeys/melvin_todo_helper.pem'
    env.user = 'ubuntu'
    env.disable_known_hosts = True


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

    system_install('python-software-properties python g++ make python-pip') #pip deps

    reqs = file(os.path.join(PROJECT_PATH, 'pip-reqs')).read().split()
    pip(reqs)

def pip_install_from_requirements_file(filename):
    sudo('sudo pip install -r %s' % os.path.join(PROJECT_PATH, filename), shell=False)

def pip(packages):
    sudo('sudo pip install %s' % ' '.join(packages), shell=False)

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

    sudo('sudo rm -rf ~/app/todo-helper')
    run('mkdir -p ~/app')
    # sudo('git clone git@github.com:p4r4digm/todo-helper.git -b sys-admin-peter ~/app/todo-helper',
    #     pty=False)

    # public repo, it works.
    sudo('git clone https://github.com/p4r4digm/todo-helper.git ~/app/todo-helper',
        pty=False)
    # run('sudo chgrp -R %s ~/app')
    run('sudo chmod -R g+wx ~/app')


@task
def config():
    put('./config/userpass.config', '~/app/todo-helper/config/userpass.config', use_sudo=True)


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
