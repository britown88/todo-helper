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

    system_install('python-software-properties python g++ make python-pip python-dev uwsgi-plugin-python') #pip deps

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

    if env.environment != 'vagrant':
        put('./config/todo-helper_deploy_key', '~/.ssh/id_rsa', use_sudo=True)

        if files.exists('~/app/todo-helper'):
            with cd('~/app/todo-helper'):
                run('git fetch --all')
                run('git reset --hard origin/master')
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


    sudo('chgrp www-data -R ~/app/')
    sudo('sudo chmod 777 ~/app/')


@task
def config():
    if env.environment != 'vagrant':
        put('./config/%s' % env.userpass_config, '~/app/todo-helper/config/userpass.config', use_sudo=True)
        put('./webapp/flaskapp/%s' % env.access_token, '~/app/todo-helper/webapp/flaskapp/access_token.txt', use_sudo=True)
        put('./webapp/flaskapp/password.txt', '~/app/todo-helper/webapp/flaskapp/password.txt', use_sudo=True)

    redisConfTemplated = render_template_file('redis.conf.jinja', {
        'rdb_location': env.rdb_location,
        'rdb_workingdir': env.rdb_workingdir
        })
    put(redisConfTemplated, '~/app/todo-helper/config/redis.conf', use_sudo=True)

    put(os.path.join(PROJECT_PATH, 'config', 'base_nginx.conf'),
        '/etc/nginx/nginx.conf',
        use_sudo=True)

    confTmpl = render_template_file('todowebapp_nginx.conf', {
        'user': env.user,
        'server_name': env.server_name,
        })
    put(confTmpl, '/etc/nginx/sites-available/todowebapp', use_sudo=True)

    if not files.exists('/etc/nginx/sites-enabled/todowebapp', use_sudo=True):
        sudo('sudo ln -s /etc/nginx/sites-available/todowebapp /etc/nginx/sites-enabled/todowebapp')

    confTmpl = render_template_file('uwsgi.ini', {
        'user': env.user,
        })
    put(confTmpl, '/etc/uwsgi/apps-available/uwsgi.ini', use_sudo=True)

    if not files.exists('/etc/uwsgi/apps-enabled/uwsgi.ini', use_sudo=True):
        sudo('sudo ln -s /etc/uwsgi/apps-available/uwsgi.ini /etc/uwsgi/apps-enabled/uwsgi.ini')


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
def restart_webapp():
    sudo('sudo service nginx restart')
    sudo('sudo service uwsgi restart')

@task
def restart_redis():
    # on my amazon machine, melvintest, this failed initially because 
    # there was a redis service running
    sudo('sudo redis-server ~/app/todo-helper/config/redis.conf')

@task
def circus_restart():
    circus_stop()
    circus_start()
    circus_status()

@task
def circus_status():
    with cd('~/app/todo-helper'):
        with prefix('source ./env/bin/activate'):
            run('circusctl status')

@task
def circus_first():
    with cd('~/app/todo-helper'):
        with prefix('source ./env/bin/activate'):
            sudo('circusd --daemon config/circus.ini')

@task
def circus_start():
    with cd('~/app/todo-helper'):
        with prefix('source ./env/bin/activate'):
            sudo('circusctl start')

@task
def circus_stop():
    with cd('~/app/todo-helper'):
        with prefix('source ./env/bin/activate'):
            run('circusctl stop')

@task
def circus_tail_log():
    with cd('~/app/todo-helper'):
        run('tail -f todo.log')


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
