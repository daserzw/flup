activate_this = '/opt/flup-dist/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/opt/flup-dist/flup/')

from flup import app

# Debug
app.debug = False
application = app

