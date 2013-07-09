from __future__ import print_function
from satella.unix import daemonize, hang_until_sig
from eunike.config import load_config
from eunike.routing import RoutingLayer
from satella.instrumentation import CounterCollection

# Load configuration
cnf = load_config()

# Check whether all modules are present

# By doing that annotate OXMs with "module" field containing
# relevant OXMInterface object
for oxmcnf in cnf['oxms']:
    try:
        oxmcnf['__module'] = __import__('eunike.oxm.%s' % (oxmcnf['type'], ),
                             (), (), 'OXMInterface', 0).OXMInterface
    except ImportError:
        print('OXM %s not installed' % (oxmcnf['type'], ))
    except:
        print('Error loading OXM %s' % (oxmcnf['type'], ))

# By doing that annotate OAMs with "module" field containing
# relevant OAMInterface object
for oamcnf in cnf['oams']:
    try:
        oamcnf['__module'] = __import__('eunike.oam.%s' % (oamcnf['type'], ),
                             (), (), 'OAMInterface', 0).OAMInterface
    except ImportError:
        print('OAM %s not installed' % (oamcnf['type'], ))
    except:
        print('Error loading OAM %s' % (oamcnf['type'], ))


# Transpose OAM and OXM's to an array of (handle, class)
oams = [(x['handle'], x['__module']) for x in cnf['oams']]
oxms = [(x['handle'], x['__module']) for x in cnf['oxms']]


# Prepare insmgr
insmgr = CounterCollection('counters')

# Prepare RL
rl = RoutingLayer(cnf, dict(oams), dict(oxms), insmgr).start()


hang_until_sig()

rl.terminate()
rl.join()

#daemonize(cnf['runas_uid'], cnf['runas_gid'])