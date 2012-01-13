from fabric.api import *
from chef import autoconfigure, Node, Search


PROJECT_NAME = '@@baseservice@@'
DOC_DIR = '/var/www/secure/sphinx/{0}'.format(PROJECT_NAME)

@task
def set_documentation_host():
    env.hosts = ['nebula.ofc.lair']


@task
def set_hosts(stage, role):
    api = autoconfigure()
    query = 'roles:{project_name}-python-{role}-node AND environment:{stage}'.format(
        project_name=PROJECT_NAME,
        stage=stage,
        role=role,
    )
    env.hosts = [row.object.attributes.get_dotted('fqdn') for
                 row in Search('node', query, api=api)]


@task
def deploy_api(dist_file):
    """Deploy the api package"""
    provision()
    _deploy_python_package(dist_file)


@task
def provision():
    """Provision the node with Chef"""
    sudo('chef-client')


@task
def deploy_docs():
    put('{0}_docs.tar.gz'.format(PROJECT_NAME), '/tmp/', mode=0666)
    run('rm -rf {0}'.format(DOC_DIR))
    run('mkdir -p {0}'.format(DOC_DIR))
    run('tar zxf /tmp/{0}_docs.tar.gz -C {1}'.format(PROJECT_NAME, DOC_DIR))
    run('chown -R :developers {0}'.format(DOC_DIR))
    run('chmod -R g+rwX {0}'.format(DOC_DIR))


def _deploy_python_package(dist_file):
    remote_path = '/tmp/{0}-latest.tar.gz'.format(PROJECT_NAME)

    sudo('rm -f {0}'.format(remote_path))
    put(dist_file, remote_path)

    pip_arguments = (
        ' --timeout=2 --use-mirrors'
        ' --find-links=https://nebula.ofc.lair/python-dist'
        ' --find-links=https://nebula.ofc.lair/python-dist/pypi'
    )

    # Install all the deps first.
    sudo(
        'pip install {0} {1}'.format(remote_path, pip_arguments)
    )

    # Install the package even if it's an update with the same name. Pip will
    # not upgrade the package if the version matches the installed version.
    # Forcing an upgrade with dependencies will re-download and install all
    # dependencies.
    sudo(
        'pip install -U {0} --no-deps {1}'.format(
            remote_path, pip_arguments)
    )
    sudo('supervisorctl reload')
    sudo('rm -f {0}'.format(remote_path))
