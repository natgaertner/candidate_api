import psycopg2 as psycopg
import psycopg2.extras as psyex
import settings
from pgloader_stripped.ersatzpg import ersatz
import os, sys, csv, json
from collections import OrderedDict,defaultdict
from datetime import datetime

def db_connect(config=settings.DATABASE_CONF):
    connstr = []
    if config.has_key('host'):
        connstr.append("host=%s" % config['host'])
    if config.has_key('port'):
        connstr.append("port=%s" % config['port'])
    if config.has_key('sslmode'):
        connstr.append("sslmode=%s" % config['sslmode'])
    connstr.append("dbname=%s user=%s password=%s" % (config['db'], config['user'], config['pw']))
    return psycopg.connect(' '.join(connstr))

def drop_database():
    return 'DROP DATABASE {db}'.format(**settings.DATABASE_CONF)

def create_database():
    return 'CREATE DATABASE {db} WITH OWNER {user} ENCODING =\'UTF8\' LC_COLLATE = \'en_US.UTF-8\' LC_CTYPE = \'en_US.UTF-8\' CONNECTION LIMIT = -1;'.format(**settings.DATABASE_CONF)

def build_database(states_dir=settings.STATE_DIR):
    states = [s for s in os.listdir(states_dir) if s.endswith('Candidates.csv')]
    state_names = [s.replace(' Candidates.csv', '') for s in states]
    print state_names
    state_dict = dict(zip(state_names, states))
    connection = db_connect()
    drop_state_tables(connection, True)
    create_state_tables(state_names, connection, True)
    create_state_tables(state_names, connection)
    errors = []
    for name, state in state_dict.iteritems():
        try:
            copy_state(name, os.path.join(states_dir,state), connection)
            update_state(name, connection)
        except Exception, error:
            import traceback; print traceback.format_exc()
            import pdb; pdb.set_trace()
            errors.append(error)
    if 'TESTONLY' in settings.__dict__ and settings.TESTONLY:
        connection.rollback()
    else:
        connection.commit()
    connection.close()
    return errors

def test_database():
    settings.TESTONLY=True
    settings.ERSATZPG_CONFIG['testonly'] = True
    return build_database()

def copy_state(state_name, state, connection):
    settings.ERSATZPG_CONFIG['tables']['candidates_import'].update({'filename':state,'table':'candidates_import_{0}'.format(state_name.lower())})
    ersatz.new_process_copies(settings, connection)

bip_tables = ['candidate','contest','candidate_in_contest','electoral_district']
class DummyModule:
    pass

def copy_bip_tables(state_name, bip_dir, connection):
    dum_set = DummyModule()
    dum_set.ERSATZPG_CONFIG = dict(settings.ERSATZPG_CONFIG)
    dum_set.ERSATZPG_CONFIG['tables'] = {}
    for bt in bip_tables:
        table_file = os.path.join(bip_dir,state_name.lower(),bt+'.csv')
        csvr = csv.reader(open(table_file,'r'))
        head = csvr.next()
        head = [(head[i],i+1) for i in range(len(head))]
        table = dict(settings.CANDIDATE_TABLE)
        table['table'] = '{bt}_import_{state}'.format(bt=bt,state=state_name.lower())
        table['columns'] = dict(head)
        table['filename'] = table_file
        dum_set.ERSATZPG_CONFIG['tables'].update({table['table']:table})
    ersatz.new_process_copies(dum_set, connection)



#    copy = ('COPY candidates_{state_name}(' + ','.join(settings.CANDIDATE_FIELDS) + ') from \'{state}\' CSV HEADER;').format(state_name=state_name,state=state)
#    connection.cursor().execute(copy)
#    connection.commit()

def update_state(state_name, connection):
    ufields = OrderedDict(settings.CANDIDATE_FIELDS)
    ufields = ','.join('{u}=candidates_import_{state_name}.{u}'.format(u=u,state_name=state_name) for u in ufields)
    cfields = OrderedDict(settings.CANDIDATE_FIELDS)
    cfields.pop('updated')
    cfields = ' or '.join('candidates_{state_name}.{u} != candidates_import_{state_name}.{u}'.format(u=u,state_name=state_name) for u in cfields)
    update = 'update candidates_{state_name} set {ufields} from candidates_import_{state_name} where candidates_{state_name}.uid = candidates_import_{state_name}.uid and ({conditions});'.format(ufields=ufields,state_name=state_name,conditions=cfields)
    insert = 'insert into candidates_{state_name}({fields}) select {fields} from candidates_import_{state_name} where candidates_import_{state_name}.uid not in (select uid from candidates_{state_name});'.format(state_name=state_name,fields=','.join(settings.CANDIDATE_FIELDS.keys()))
    print update
    print insert
    connection.cursor().execute(update)
    connection.cursor().execute(insert)

def create_state_tables(states, connection, imp=False):
    imp_string = '_import' if imp else ''
    seq = 'CREATE SEQUENCE pksq{imp} START 1;'.format(imp=imp_string)
    master = 'CREATE TABLE IF NOT EXISTS candidates{imp} (id int4 DEFAULT nextval(\'pksq{imp}\'),'.format(imp=imp_string)
    master+=','.join('{name} {type}'.format(name=k,type=v) for k,v in settings.CANDIDATE_FIELDS.iteritems())
    master += ');'
    children = ''.join('CREATE TABLE IF NOT EXISTS candidates{imp}_{state} (CHECK (trim({state_field}) ~* \'{state}\')) INHERITS (candidates{imp});'.format(state=s,state_field=settings.STATE_FIELD, imp=imp_string) for s in states)
    drop_trigger = 'DROP TRIGGER IF EXISTS insert_candidate_trigger{imp} on candidates{imp}'.format(imp=imp_string)
    trigger = 'CREATE TRIGGER insert_candidate_trigger{imp} BEFORE INSERT on candidates{imp} FOR EACH ROW EXECUTE PROCEDURE candidate_insert_trigger{imp}();'.format(imp=imp_string)
    function = 'CREATE OR REPLACE FUNCTION candidate_insert_trigger{imp}() RETURNS TRIGGER AS $$ BEGIN IF '.format(imp=imp_string)+ ' ELSEIF '.join('trim(NEW.{state_field}) ~* \'{state}\' THEN INSERT INTO candidates{imp}_{state} VALUES (NEW.*);'.format(state=s, state_field=settings.STATE_FIELD, imp=imp_string) for s in states) + ' ELSE RAISE EXCEPTION \'NO SUCH STATE IN DATABASE\'; END IF; RETURN NULL; END; $$ LANGUAGE plpgsql;'
    print master
    print children
    cur = connection.cursor()
#    cur.execute('BEGIN;')
    cur.execute("SELECT c.relname from pg_class c where c.relkind = 'S';")
    sqs = cur.fetchall()
    print sqs
    if ('pksq{imp}'.format(imp=imp_string),) not in sqs:
        cur.execute(seq)
    cur.execute(master)
    cur.execute(children)
    cur.execute(function)
    cur.execute(drop_trigger)
    cur.execute(trigger)
#    cur.execute('END;')
    cur.close()

    if 'TESTONLY' in settings.__dict__ and settings.TESTONLY:
        pass
        #connection.rollback()
    else:
        connection.commit()

def drop_state_tables(connection, imp=False):
    cur = connection.cursor()
#    cur.execute('BEGIN;')
    imp_string = '_import' if imp else ''
    cur.execute('DROP TABLE IF EXISTS candidates{imp} CASCADE;'.format(imp=imp_string))
    cur.execute('DROP FUNCTION IF EXISTS candidate{imp}_insert_trigger();'.format(imp=imp_string))
    cur.execute('DROP SEQUENCE IF EXISTS pksq{imp};'.format(imp=imp_string))
#    cur.execute('END;')
    cur.close()
    if 'TESTONLY' in settings.__dict__ and settings.TESTONLY:
        pass
        #connection.rollback()
    else:
        connection.commit()

def query_candidates(query_fields):
    u = query_fields.pop('updated',None)
    day_format = '%Y-%m-%d'
    time_format = '%H-%M-%S'
    updated_query = []
    if u != None:
        if u == 'notnull':
            updated_query = 'updated is not null'
        elif u.lower() == 'null':
            updated_query = 'updated is null'
        else:
            try:
                d = datetime.strptime(u,day_format)
            except:
                d = datetime.strptime(u,day_format+'T'+time_format)
            t = psycopg.Timestamp(d.year,d.month,d.day,d.hour,d.minute,d.second).getquoted()
            updated_query = 'updated > {t}'.format(t=t)
        updated_query = [updated_query]
    fields = OrderedDict(settings.CANDIDATE_FIELDS)
    fields = ','.join((k if not v=='timestamp' else "to_char({k}, 'YYYY-MM-DD HH24:MI:SS') as {k}".format(k=k)) for k,v in fields.iteritems())
    sql = 'SELECT {fields} from candidates where '.format(fields=fields) + ' and '.join(["{0} ilike '%{1}%'".format(k,v) for (k,v) in query_fields.iteritems()] + updated_query) + ';'
    print sql
    connection = db_connect()
    cur = connection.cursor(cursor_factory=psyex.RealDictCursor)
    cur.execute(sql)
    return cur.fetchall()

def query_bip(table, query_fields):
    u = query_fields.pop('updated',None)
    day_format = '%Y-%m-%d'
    time_format = '%H-%M-%S'
    updated_query = []
    if u != None:
        if u == 'notnull':
            updated_query = 'updated is not null'
        elif u.lower() == 'null':
            updated_query = 'updated is null'
        else:
            try:
                d = datetime.strptime(u,day_format)
            except:
                d = datetime.strptime(u,day_format+'T'+time_format)
            t = psycopg.Timestamp(d.year,d.month,d.day,d.hour,d.minute,d.second).getquoted()
            updated_query = 'updated > {t}'.format(t=t)
        updated_query = [updated_query]
    fields = OrderedDict(settings.__dict__['BIP_{table}_FIELDS'.format(table=table.upper())])
    fields = ','.join((k if not v=='timestamp' else "to_char({k}, 'YYYY-MM-DD HH24:MI:SS') as {k}".format(k=k)) for k,v in fields.iteritems())
    sql = 'SELECT {fields} from {table} where '.format(fields=fields,table=table) + ' and '.join(["{0} ilike '%{1}%'".format(k,v) for (k,v) in query_fields.iteritems()] + updated_query) + ';'
    print sql
    connection = db_connect(settings.BIP_DATABASE_CONF)
    cur = connection.cursor(cursor_factory=psyex.RealDictCursor)
    cur.execute(sql)
    return cur.fetchall()

electoraldistrict_fields = 'election_key,name,number,source,state_id,type,id,identifier,updated'.split(',')
contest_fields = 'number_voting_for,election_key,electoral_district_id,office,filing_closed_date,type,electoral_district_type,number_elected,custom_ballot_heading,contest_type,electorate_specifications,write_in,source,state,electoral_district_name,ballot_placement,partisan,primary_party,election_id,id,special,identifier,updated'.split(',')
candidate_fields = 'filed_mailing_address,election_key,name,phone,mailing_address,facebook_url,youtube,email,candidate_url,source,google_plus_url,twitter_name,incumbent,party,wiki_word,id,biography,photo_url,identifier,updated'.split(',')
#ed_fields = ','.join('ed.{f} as ed_{f}'.format(f=f) for f in electoraldistrict_fields)
#ca_fields = ','.join('ca.{f} as ca_{f}'.format(f=f) for f in candidate_fields)
#co_fields = ','.join('co.{f} as co_{f}'.format(f=f) for f in contest_fields)

def query_merged_bip(query_fields):
    day_format = '%Y-%m-%d'
    time_format = '%H-%M-%S'
    updated_queries = defaultdict(lambda:[])
    for table in ['candidate','contest','electoral_district']:
        u = query_fields.pop(table+'.updated',None)
        if u != None:
            if u == 'notnull':
                updated_query = 'updated is not null'
            elif u.lower() == 'null':
                updated_query = 'updated is null'
            else:
                try:
                    d = datetime.strptime(u,day_format)
                except:
                    d = datetime.strptime(u,day_format+'T'+time_format)
                t = psycopg.Timestamp(d.year,d.month,d.day,d.hour,d.minute,d.second).getquoted()
                updated_query = table+'.updated > {t}'.format(t=t)
            updated_queries[table] = [updated_query]
    table_query_fields = defaultdict(lambda:{})
    where_dict = defaultdict(lambda:'')
    for k,v in query_fields.iteritems():
        table_query_fields[k[:k.index('.')]].update({k:v})
        where_dict[k[:k.index('.')]] = ' where '
    ca_fields = OrderedDict(settings.__dict__['BIP_CANDIDATE_FIELDS'.format(table=table.upper())])
    ca_fields = ','.join(('ca.'+k+' as ca_'+k if not v=='timestamp' else "to_char(ca.{k}, 'YYYY-MM-DD HH24:MI:SS') as ca_{k}".format(k=k)) for k,v in ca_fields.iteritems())
    co_fields = OrderedDict(settings.__dict__['BIP_CONTEST_FIELDS'.format(table=table.upper())])
    co_fields = ','.join(('co.'+k+' as co_'+k if not v=='timestamp' else "to_char(co.{k}, 'YYYY-MM-DD HH24:MI:SS') as co_{k}".format(k=k)) for k,v in co_fields.iteritems())
    ed_fields = OrderedDict(settings.__dict__['BIP_ELECTORAL_DISTRICT_FIELDS'.format(table=table.upper())])
    ed_fields = ','.join(('ed.'+k+' as ed_'+k if not v=='timestamp' else "to_char(ed.{k}, 'YYYY-MM-DD HH24:MI:SS') as ed_{k}".format(k=k)) for k,v in ed_fields.iteritems())
    sql = 'SELECT {ca_fields},{co_fields},{ed_fields}'.format(ca_fields=ca_fields, co_fields=co_fields,ed_fields=ed_fields) + ' from (select * from contest' + where_dict['contest'] + ' and '.join(["{0} ilike '%{1}%'".format(k,v) for k,v in table_query_fields['contest'].iteritems()] + updated_queries['contest'])
    sql += ') as co join candidate_in_contest as cic on co.id = cic.contest_id join (select * from candidate' + where_dict['candidate'] + ' and '.join(["{0} ilike '%{1}%'".format(k,v) for k,v in table_query_fields['candidate'].iteritems()] + updated_queries['candidate']) 
    sql += ') as ca on cic.candidate_id = ca.id join (select * from electoral_district' + where_dict['electoral_district'] + ' and '.join(["{0} ilike '%{1}%'".format(k,v) for k,v in table_query_fields['electoral_district'].iteritems()] + updated_queries['electoral_district']) + ') as ed on co.electoral_district_id = ed.id;'
    print sql
    connection = db_connect(settings.BIP_DATABASE_CONF)
    cur = connection.cursor(cursor_factory=psyex.RealDictCursor)
    cur.execute(sql)
    return cur.fetchall()

def dump_json(nulls=False):
    connection = db_connect(settings.BIP_DATABASE_CONF)
    cur = connection.cursor(cursor_factory=psyex.RealDictCursor)
    for table in ['candidate','contest','candidate_in_contest','electoral_district','referendum','ballot_response']:
        fields = OrderedDict(settings.__dict__['BIP_{table}_FIELDS'.format(table=table.upper())])
        fields = ','.join((k if not v=='timestamp' else "to_char({k}, 'YYYY-MM-DD HH24:MI:SS') as {k}".format(k=k)) for k,v in fields.iteritems())
        sql = 'SELECT {fields} from {table};'.format(fields=fields,table=table) 
        print sql
        cur.execute(sql)
        with open(table+'.json','w') as f:
            if nulls:
                f.write(json.dumps(cur.fetchall()))
            else:
                f.write(json.dumps(map(lambda d: dict((k,v) for k,v in d.iteritems() if v != None),cur.fetchall())))


if __name__=='__main__':
    if 'drop' in sys.argv:
        print drop_database()
    if 'create' in sys.argv:
        print create_database()
    if 'build' in sys.argv:
        build_database()
    if 'json' in sys.argv:
        dump_json()
