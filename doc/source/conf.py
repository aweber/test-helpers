import sys, os

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
sys.path.insert(0, os.path.abspath('.'))

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

html_theme = 'nature'

intersphinx_mapping = {
    'http://docs.python.org/': None,
}

master_doc = 'index'
todo_include_todos = True

source_suffix = '.rst'
project = '@@baseservice@@'
