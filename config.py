import sys, json, copy
import re
from warnings import warn

DEFAULTS = {'runas_uid': None, 
            'runas_gid': None,
            }

DEFAULTS_FOR_OXM = {
    'regexes': [r'(.*)'],
    'priority': 0,
    'backup': False
}

def load_config():
    # Load configuration
    with open(sys.argv[1], 'rb') as json_config:
        cnf = json.load(json_config)

    config = copy.deepcopy(DEFAULTS)
    config.update(cnf)

    new_oxm = []
    for oxm in config['oxms']:
        nox = copy.deepcopy(DEFAULTS_FOR_OXM)
        nox.update(oxm)
        new_oxm.append(nox)
    config['oxms'] = new_oxm


    return config
