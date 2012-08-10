from collections import OrderedDict
DATABASE_CONF={
    'db':'candidatedb',
    'user':'postgres',
    'pw':'expcand'
    }
STATE_FIELD = 'state'
STATE_DIR = '/home/gaertner/code/candidateview/candidate_files/trimmed'

CANDIDATE_TABLE = {
        'skip_head_lines':1,
        'format':'csv',
        'field_sep':',',
        'quotechar':'"',
        'copy_every':500000,
        'table':'candidates',
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
            'youtube':18
            }
        }
ERSATZPG_CONFIG = {'debug':True}
ERSATZPG_CONFIG.update(DATABASE_CONF)
ERSATZPG_CONFIG.update({
    'tables':{
        'candidates':CANDIDATE_TABLE
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
    ('completed','bool'),
    ('incumbent','bool'),
    ('phone','varchar(100)'),
    ('mailing_address','varchar(255)'),
    ('website','text'),
    ('email','varchar(50)'),
    ('facebook_url','text'),
    ('twitter_name','varchar(20)'),
    ('google_plus','text'),
    ('wiki_word','varchar(100)'),
    ('youtube','text')
    ])
