from fabric.api import *

env.hosts = ['nebula.ofc.lair']

PROJECT_NAME = 'baseservice'
DIST_DIR = '/var/www/secure/python-dist/'
DOC_DIR = '/var/www/secure/sphinx/{0}'.format(PROJECT_NAME)

def upload_package():
    put('dist/{0}*.tar.gz'.format(PROJECT_NAME), DIST_DIR)

def deploy_docs():
    put('{0}_docs.tar.gz'.format(PROJECT_NAME), '/tmp/', mode=0666)
    run('rm -rf {0}'.format(DOC_DIR))
    run('mkdir -p {0}'.format(DOC_DIR))
    run('tar zxf /tmp/{0}_docs.tar.gz -C {1}'.format(PROJECT_NAME, DOC_DIR))
    run('chown -R :developers {0}'.format(DOC_DIR))
    run('chmod -R g+rwX {0}'.format(DOC_DIR))
