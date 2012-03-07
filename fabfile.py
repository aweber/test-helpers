from fabric.api import *
from chef import autoconfigure, Node, Search


PROJECT_NAME = '@@project_name@@'
DOC_DIR = '/var/www/docs/{0}'.format(PROJECT_NAME)


def _set_username_password():
    """Sets the username and password in the fabric env."""
    # Override username/password here, if necessary


@task
def set_documentation_host():
    env.hosts = ['docs.colo.lair']


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
    _set_username_password()
    provision()
    _deploy_python_package(dist_file)


@task
def provision():
    """Provision the node with Chef"""
    sudo('chef-client')


@task
def deploy_docs(project_name, version):
    """Deploy the documentation"""

    docs_base = '{0}/{1}'
    docs_path = docs_base.format(DOC_DIR, version)
    tar = '{0}_docs.tar.gz'.format(project_name)
    link_to_latest = False

    put(tar, '/tmp/', mode=0666)
    run('rm -rf {0}'.format(docs_path))
    run('mkdir -p {0}'.format(docs_path))
    run('tar zxf /tmp/{0} -C {1}'.format(tar, docs_path))

    if not version.find('-'):
        link_to_latest = True
        docs_link = docs_base.format(DOC_DIR, 'production')
    else:
        docs_link = docs_base.format(DOC_DIR, 'staging')

    run('rm -rf {0}'.format(docs_link))
    run('chown -R :www-data {0}'.format(docs_path))
    run('chmod -R 775 {0}'.format(docs_path))
    run('ln -s {0} {1}'.format(docs_path, docs_link))
    if link_to_latest:
        latest_link = docs_base.format(DOC_DIR, 'latest')
        run('ln -s {0} {1}'.format(docs_path, latest_link))


def _deploy_python_package(dist_file):
    remote_path = '/tmp/{0}-latest.tar.gz'.format(PROJECT_NAME)

    sudo('rm -f {0}'.format(remote_path))
    put(dist_file, remote_path)

    pip_arguments = (' --timeout=2 --use-mirrors')

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
