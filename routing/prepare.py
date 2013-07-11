from eunike.objects import EIOOAM, EIOOXM
from eunike.routing.backendmgr import BackendManager
from satella.instrumentation import CounterCollection

def register_objects(rlayer, confobjs, oams, oxms, insmgr):
    """
    Called as part of Routing Layer initialization

    @type oams: dict(handle::str => OAMInterface)
    @type oxms: dict(handle::str => OXMInterface)
    @param insmgr: root CounterCollection
    """

    eio_oam = {}
    bem = BackendManager(rlayer)

    for handle, oamcls in oams.items():
        sec, = [x for x in confobjs['oams'] if x['handle'] == handle]
        cc = CounterCollection('a-%s' % (handle, ), u'OAM %s' % (handle, ))
        insmgr.add(cc)
        io = EIOOAM(handle, rlayer, bem)
        eio_oam[handle] = oamcls(io, sec, cc), io, sec, cc

    eio_oxm = {}

    for handle, oxmcls in oxms.items():
        sec, = [x for x in confobjs['oxms'] if x['handle'] == handle]
        cc = CounterCollection('x-%s' % (handle, ), u'OXM %s' % (handle, ))
        insmgr.add(cc)
        io = EIOOXM(handle, rlayer, bem)
        eio_oxm[handle] = oxmcls(io, sec, cc), io, sec, cc

    bem.add_backends(eio_oam, eio_oxm)

    rlayer.bm = bem

