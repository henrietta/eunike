from __future__ import print_function
from satella.unix import hang_until_sig
from eunike.config import load_config
from eunike.routing import RoutingLayer
from eunike.instrumentation import InstrumentationSaverThread
from satella.instrumentation import CounterCollection
import sys

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
        sys.exit()        
    except:
        print('Error loading OXM %s' % (oxmcnf['type'], ))
        sys.exit()

# By doing that annotate OAMs with "module" field containing
# relevant OAMInterface object
for oamcnf in cnf['oams']:
    try:
        oamcnf['__module'] = __import__('eunike.oam.%s' % (oamcnf['type'], ),
                             (), (), 'OAMInterface', 0).OAMInterface
    except ImportError:
        print('OAM %s not installed' % (oamcnf['type'], ))
        sys.exit()
    except:
        print('Error loading OAM %s' % (oamcnf['type'], ))
        sys.exit()

# Transpose OAM and OXM's to an array of (handle, class)
oams = [(x['handle'], x['__module']) for x in cnf['oams']]
oxms = [(x['handle'], x['__module']) for x in cnf['oxms']]

# Prepare OSM
try:
    osm = __import__('eunike.osm.%s' % (cnf['osm']['type'], ), 
                     (), (), 'OSMInterface', 0).OSMInterface(
                     cnf['osm'])
    osm.i_start()
except ImportError:
    print('Failed to load OSM')
    sys.exit()


# Prepare insmgr
insmgr = CounterCollection('counters')

# Prepare saver thread (if necessary)
if 'instrumentation' in cnf:
    if cnf['instrumentation']['enabled']:
        saver = InstrumentationSaverThread(insmgr, cnf['instrumentation'])
        saver.start()


# Prepare RL
rl = RoutingLayer(cnf, dict(oams), dict(oxms), insmgr, osm).start()

hang_until_sig()

try:
    saver.terminate()
except:
    pass
rl.terminate()
osm.i_stop()
rl.join()
osm.i_join()
try:
    saver.join()
except:
    pass
