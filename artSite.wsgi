activate_this = '/home/grygon/.virtualenvs/artSite/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
 
sys.path.insert(0,'/home/grygon/artSite/py/')
 
from main import app as application
