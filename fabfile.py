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
def melvinlive(app='all'):
    env.update(APP_ENV['melvinlive'])

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

    node()

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
    jinja_env = Environment(loader=FileSystemLoader('config'))
    tmpl = jinja_env.get_template(filename)
    return StringIO(tmpl.render(nginxVars))

def node():
    # ppa repo for node 0.8.23
    sudo('sudo add-apt-repository ppa:chris-lea/node.js-legacy --remove', pty=False, quiet=True)
    sudo('sudo add-apt-repository ppa:chris-lea/node.js', pty=False, quiet=True)
    system_update()

    system_install('nodejs')
    sudo('apt-get -yqq remove coffeescript')

    # `npm install` uses this folder sometimes, and will complain if it doesn't have proper access.
    sudo('mkdir -p ~/tmp')
    sudo('chmod 0777 ~/tmp')

    # install global requirements
    sudo('npm install -g grunt-cli coffee-script bower')



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

    redisConfTemplated = render_template_file('redis.conf.jinja', {'rdb_location': env.rdb_location})
    put(redisConfTemplated, '~/app/todo-helper/config/redis.conf', use_sudo=True)

    # put('./config/circus.conf', '/etc/init/circus.conf', use_sudo=True)
    # put('./config/circus.ini', '/etc/circus.ini', use_sudo=True)




@task
def webapp_build():
    with cd('~/app/todo-helper/webapp'):
        run('npm install')
        run('bower install')
        run('grunt browserify')


##############################################
# restart_all task, and it's related subtasks
# Restart nginx
# restart circus or python
##############################################

@task
def restart_all():
    restart_nginx()
    restart_redis()

@task
def restart_redis():
    sudo('redis-server ~/app/todo-helper/config/redis.conf')

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

@task
def restart_circus():
    stop_circusd()
    start_circusd()
    circus_status()

@task
def circus_status():
    with cd('~/app/todo-helper'):
        with prefix('source ./env/bin/activate'):
            run('circusctl status')

@task
def start_circus():
    with cd('~/app/todo-helper'):
        with prefix('source ./env/bin/activate'):
            run('circusd --daemon config/circus.ini')

@task
def stop_circusd():
    with cd('~/app/todo-helper'):
        with prefix('source ./env/bin/activate'):
            run('circusctl stop')


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
