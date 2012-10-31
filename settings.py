from collections import OrderedDict
from datetime import datetime
import psycopg2 as psycopg
import pwsettings
DATABASE_CONF={
    'db':'candidatedb',
    'user':'postgres',
    'pw':pwsettings.password,
    }
BIP_DATABASE_CONF={
    'db':'bip',
    'user':'postgres',
    'pw':pwsettings.password,
    }
TESTONLY = False
STATE_FIELD = 'state'
STATE_DIR = '/home/gaertner/Dropbox/BIP Production'

def nowtime():
    d = datetime.now()
    return d.strftime('%Y-%m-%dT%H:%M:%S'),

CANDIDATE_TABLE = {
        'skip_head_lines':1,
        'format':'csv',
        'field_sep':',',
        'quotechar':'"',
        'copy_every':500000,
        'table':'candidates_import',
        'columns':{
            'uid':1,
            'state':2,
            'office_level':3,
            'electoral_district':4,
            'office_name':5,
            'candidate_name':6,
            'candidate_party':7,
            'completed':8,
            'incumbent':9,
            'phone':10,
            'mailing_address':11,
            'website':12,
            'email':13,
            'facebook_url':14,
            'twitter_name':15,
            'google_plus':16,
            'wiki_word':17,
            'youtube':18,
            'updated':{'function':nowtime,'columns':()},
            }
        }
ERSATZPG_CONFIG = {'debug':True, 'use_utf':True, 'testonly':TESTONLY}
ERSATZPG_CONFIG.update(DATABASE_CONF)
ERSATZPG_CONFIG.update({
    'tables':{
        'candidates_import':CANDIDATE_TABLE
        }
    })


CANDIDATE_FIELDS=OrderedDict([
    ('uid','varchar(10)'),
    ('state','varchar(3)'),
    ('office_level','varchar(50)'),
    ('electoral_district','text'),
    ('office_name','text'),
    ('candidate_name','varchar(200)'),
    ('candidate_party','varchar(50)'),
    ('completed','varchar(50)'),
    ('incumbent','bool'),
    ('phone','varchar(100)'),
    ('mailing_address','varchar(255)'),
    ('website','text'),
    ('email','varchar(100)'),
    ('facebook_url','text'),
    ('twitter_name','text'),
    ('google_plus','text'),
    ('wiki_word','varchar(100)'),
    ('youtube','text'),
    ('updated','timestamp'),
    ])

REFERENDUM_FIELDS = OrderedDict([
    ("id", 'int4'),
    ("source", 'text'),
    ("title", 'text'),
    ("subtitle", 'text'),
    ("brief", 'text'),
    ("text", 'varchar(255)'),
    ("pro_statement", 'varchar(255)'),
    ("con_statement", 'varchar(255)'),
    ("contest_id", 'int4'),
    ("passage_threshold", 'varchar(255)'),
    ("effect_of_abstain", 'varchar(255)'),
    ("election_key", 'int4'),
    ("updated", 'timestamp'),
    ("identifier", 'text'),])

BALLOT_RESPONSE_FIELDS = OrderedDict([
    ("id", 'int4'),
    ("source", 'text'),
    ("referendum_id", 'int4'),
    ("sort_order", 'varchar(255)'),
    ("text", 'text'),
    ("election_key", 'int4'),
    ("updated", 'timestamp'),
    ("identifier", 'text'),])

BIP_CANDIDATE_FIELDS=OrderedDict([
    ('id', 'int4'), ('source', 'text'), ('name', 'varchar(255)'), ('party', 'varchar(255)'), ('candidate_url', 'varchar(255)'), ('biography', 'varchar(255)'), ('phone', 'varchar(255)'), ('photo_url', 'varchar(255)'), ('filed_mailing_address', 'int4'), ('mailing_address', 'text'), ('email', 'varchar(255)'), ('incumbent', 'bool'), ('google_plus_url', 'varchar(255)'), ('twitter_name', 'varchar(255)'), ('facebook_url', 'varchar(255)'), ('wiki_word', 'varchar(255)'), ('youtube', 'text'), ('election_key', 'int4'), ('identifier', 'text'), ('updated','timestamp'),
    ])

BIP_CONTEST_FIELDS = OrderedDict([
    ('id', 'int4'), ('source', 'text'), ('election_id', 'int4'), ('electoral_district_id', 'int4'), ('electoral_district_name', 'varchar(255)'), ('electoral_district_type', 'varchar(255)'), ('partisan', 'bool'), ('type', 'varchar(255)'), ('primary_party', 'varchar(255)'), ('electorate_specifications', 'varchar(255)'), ('special', 'bool'), ('office', 'varchar(255)'), ('filing_closed_date', 'date'), ('number_elected', 'int4'), ('number_voting_for', 'int4'), ('ballot_placement', 'varchar(255)'), ('contest_type', 'contestenum'), ('write_in', 'bool'), ('custom_ballot_heading', 'text'), ('election_key', 'int4'), ('state', 'varchar(5)'), ('identifier', 'text'), ('updated','timestamp'),('office_level','varchar(255)'),('ed_matched','bool'),
    ])

BIP_CANDIDATE_IN_CONTEST_FIELDS = OrderedDict([
    ('source', 'text'), ('election_key', 'int4'), ('sort_order', 'int4'), ('contest_id', 'int4'), ('candidate_id', 'int4')
    ])

BIP_ELECTORAL_DISTRICT_FIELDS = OrderedDict([
    ('id', 'int4'), ('source', 'text'), ('name', 'varchar(255)'), ('type', 'varchar(255)'), ('number', 'int4'), ('state_id', 'int4'), ('election_key', 'int4'), ('identifier', 'text'), ('updated','timestamp'),
    ])
BIP_REFERENDUM_FIELDS = OrderedDict([
    ("id", 'int4'),
    ("source", 'text'),
    ("title", 'text'),
    ("subtitle", 'text'),
    ("brief", 'text'),
    ("text", 'varchar(255)'),
    ("pro_statement", 'varchar(255)'),
    ("con_statement", 'varchar(255)'),
    ("contest_id", 'int4'),
    ("passage_threshold", 'varchar(255)'),
    ("effect_of_abstain", 'varchar(255)'),
    ("election_key", 'int4'),
    ("updated", 'timestamp'),
    ("identifier", 'text'),])

BIP_BALLOT_RESPONSE_FIELDS = OrderedDict([
    ("id", 'int4'),
    ("source", 'text'),
    ("referendum_id", 'int4'),
    ("sort_order", 'varchar(255)'),
    ("text", 'text'),
    ("election_key", 'int4'),
    ("updated", 'timestamp'),
    ("identifier", 'text'),])

