import traceback, logging
from io import StringIO

#========================================
def logException(message, error_mode = True, limit_stack = 20):
    rep = StringIO()
    traceback.print_exc(file = rep, limit = limit_stack)
    if error_mode:
        logging.error(message + "\n" + rep.getvalue())
    else:
        logging.warning(message + "\n" + rep.getvalue())
