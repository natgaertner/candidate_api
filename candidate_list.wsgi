activate_this = '/home/gaertner/code/candidateview/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from candidate_list import app as application
import logging, sys
logging.basicConfig(stream=sys.stderr)
