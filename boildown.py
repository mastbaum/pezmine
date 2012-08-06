'''reduce tests to their essence.

these functions take a test document and a (db) id, flatten the subset of the
results pertaining to the db, and return them as a dict. the assumption is that
each key in the test, regardless of depth, has equal weight in the distance
measure. clusters get fuzzed out by statistical fluctuations in the parameters,
but it would be hard to weight these without risking poor clustering of a subtle
problem.
'''

def get_db_id(config, id):
    '''given a configuration (as found in test documents) and a db id, find
    the db slot number.
    '''
    slot = None
    for db in config['db']:
        if db['db_id'] == id:
            slot = db['slot']
            break
    return slot

def chinj_scan(doc, id):
    slot = get_db_id(doc['config'], id)
    d = {}
    fields = ['%s_%s' % (i, j) for j in ('even', 'odd') for i in ('QHL', 'QHS', 'QLX', 'TAC', 'errors')]
    for field in fields:
        for i, o in enumerate(doc[field][8*slot:8*slot+8] if slot else doc[field]):
            if field.startswith('errors'):
                o = map(int, o)
            for j, p in enumerate(o):
                k = '%s__%i__%i' % (field, i, j)
                d[k] = p

    return d

def cmos_m_gtvalid(doc, id):
    slot = get_db_id(doc['config'], id)
    d = {}
    for i, o in enumerate(doc['channels'][8*slot:8*slot+8] if slot else doc['channels']):
        if 'id' in o:
            del o['id']
        o['errors'] = int(o['errors'])
        for k, v in o.iteritems():
            doc['%s__%i' % (k, i)] = v
    d['iseta'] = doc['iseta']
    d['isetm'] = doc['isetm']
    d['slot_errors'] = doc['slot_errors']
    d['tacref'] = doc['tacref']
    d['vmax'] = doc['vmax']

    return d

def crate_cbal(doc, id):
    slot = get_db_id(doc['config'], id)
    d = {}
    for i, o in enumerate(doc['channels'][8*slot:8*slot+8] if slot else doc['channels']):
        if 'id' in o:
            del o['id']
        if 'error_flags' in o:
            del o['error_flags']
        o['errors'] = int(o['errors'])
        for k, v in o.iteritems():
            d['%s__%i' % (k, i)] = v

    return d

def disc_check(doc, id):
    slot = get_db_id(doc['config'], id)
    d = {}
    for i, o in enumerate(doc['channels'][8*slot:8*slot+8] if slot else doc['channels']):
        if 'id' in o:
            del o['id']
        o['errors'] = int(o['errors'])
        for k, v in o.iteritems():
            d['%s__%i' % (k, i)] = v

    return d

# fec
# not yet used... need to think about this
#def cald_test(doc):
#    return {
#        'cald_test__adc_0': doc['adc_0'],
#        'cald_test__adc_1': doc['adc_1'],
#        'cald_test__adc_2': doc['adc_2'],
#        'cald_test__adc_3': doc['adc_3'],
#        'cald_test__dac_value': doc['dac_value']
#    }

#def cgt_test(doc):
#    return {
#        'cgt_test__errors': map(int, doc['errors']),
#        'cgt_test__missing_bundles': int(doc['missing_bundles'])
#    }

