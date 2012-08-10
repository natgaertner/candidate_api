import psycopg2 as psycopg
import psycopg2.extras as psyex
import settings
import ersatz
import os, sys

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
    state_dict = dict(zip(state_names, states))
    connection = db_connect()
    drop_state_tables(connection)
    create_state_tables(state_names, connection)
    for name, state in state_dict.iteritems():
        copy_state(name, os.path.join(states_dir,state))
    connection.close()

def copy_state(state_name, state):#, connection):
    settings.ERSATZPG_CONFIG['tables']['candidates'].update({'filename':state,'table':'candidates_{0}'.format(state_name.lower())})
    ersatz.new_process_copies(settings)
#    copy = ('COPY candidates_{state_name}(' + ','.join(settings.CANDIDATE_FIELDS) + ') from \'{state}\' CSV HEADER;').format(state_name=state_name,state=state)
#    connection.cursor().execute(copy)
#    connection.commit()


def create_state_tables(states, connection):
    seq = 'CREATE SEQUENCE pksq START 1;'
    master = 'CREATE TABLE candidates (id int4 DEFAULT nextval(\'pksq\'),'
    master+=','.join('{name} {type}'.format(name=k,type=v) for k,v in settings.CANDIDATE_FIELDS.iteritems())
    master += ');'
    children = ''.join('CREATE TABLE candidates_{state} (CHECK (trim({state_field}) ~* \'{state}\')) INHERITS (candidates);'.format(state=s,state_field=settings.STATE_FIELD) for s in states)
    trigger = 'CREATE TRIGGER insert_candidate_trigger BEFORE INSERT on candidates FOR EACH ROW EXECUTE PROCEDURE candidate_insert_trigger();'
    function = 'CREATE OR REPLACE FUNCTION candidate_insert_trigger() RETURNS TRIGGER AS $$ BEGIN IF '+ ' ELSEIF '.join('trim(NEW.{state_field}) ~* \'{state}\' THEN INSERT INTO candidates_{state} VALUES (NEW.*);'.format(state=s, state_field=settings.STATE_FIELD) for s in states) + ' ELSE RAISE EXCEPTION \'NO SUCH STATE IN DATABASE\'; END IF; RETURN NULL; END; $$ LANGUAGE plpgsql;'
    cur = connection.cursor()
#    cur.execute('BEGIN;')
    cur.execute(seq)
    cur.execute(master)
    cur.execute(children)
    cur.execute(function)
    cur.execute(trigger)
#    cur.execute('END;')
    cur.close()
    connection.commit()

def drop_state_tables(connection):
    cur = connection.cursor()
#    cur.execute('BEGIN;')
    cur.execute('DROP TABLE IF EXISTS candidates CASCADE;')
    cur.execute('DROP FUNCTION IF EXISTS candidate_insert_trigger();')
    cur.execute('DROP SEQUENCE IF EXISTS pksq;')
#    cur.execute('END;')
    cur.close()
    connection.commit()

def query_candidates(query_fields):
    sql = 'SELECT * from candidates where ' + ' and '.join("{0} ilike '%{1}%'".format(k,v) for (k,v) in query_fields) + ';'
    connection = db_connect()
    cur = connection.cursor(cursor_factory=psyex.RealDictCursor)
    cur.execute(sql)
    return cur.fetchall()


if __name__=='__main__':
    if 'drop' in sys.argv:
        print drop_database()
    if 'create' in sys.argv:
        print create_database()
    if 'build' in sys.argv:
        build_database()
