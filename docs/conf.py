import os

import test_helpers

project = 'test-helpers'
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'tornado': ('http://www.tornadoweb.org/en/latest/', None),
    'psycopg2': ('http://initd.org/psycopg/docs/', None),
}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
]

copyright = 'AWeber Communications'
pygments_style = 'sphinx'

templates_path = ['_templates']
exclude_trees = ['build']
html_static_path = ['_static']


# Only import RTD theme locally, it's the default on readthedocs.org
if not os.environ.get('READTHEDOCS', False):
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


master_doc = 'index'
todo_include_todos = True
version = test_helpers.__version__
release = version

source_suffix = '.rst'
