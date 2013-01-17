from flask import Flask
import json, os, re, hashlib,datetime, gdbm, random
from collections import defaultdict
from flask import request, session, redirect,url_for, render_template
from flaskext.autoindex import AutoIndex
from sql_utils import query_candidates, test_database, build_database, query_bip, query_merged_bip
import basic_auth
import pwsettings
import psycopg2 as psycopg
from psycopg2.extensions import QuotedString
app = Flask(__name__)
ai = AutoIndex(app, browse_root='/home/gaertner/Dropbox/BIP Production')
app.secret_key = pwsettings.secret_key

query_params = ['state','office_level','electoral_district','office_name','candidate_name','candidate_party','updated']

connstr = "dbname=users user=postgres password="+pwsettings.password
connection = psycopg.connect(connstr)

@app.route('/isloggedin')
def is_logged():
    if 'username' in session:
        return '1'
    else:
        return '0'

@app.route('/')
@app.route('/<path:path>')
def list_dir(path='.'):
    print session
    if 'username' not in session:
        return render_template('index_template.html')
    else:
        return ai.render_autoindex(path, template='autoindex.html')

@app.route('/api_dir/')
@app.route('/api_dir/<path:path>')
def api_dir(path='.'):
    if 'username' not in session:
        return ''
    else:
        return ai.render_autoindex(path, template='aicontent.html')

@app.route('/is_file/')
@app.route('/is_file/<path:path>')
def is_file(path='.'):
    if 'username' not in session:
        return '0'
    else:
        path = re.sub(r'\/*$','',path)
        abspath = os.path.join(ai.rootdir.abspath, path)
        return '0' if os.path.isdir(abspath) else '1'

for i in app.url_map.iter_rules():
    if i.rule == '/' or i.rule == '/<path:path>':
        i.endpoint='list_dir'

app.view_functions['list_dir'] = list_dir

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('username')
    return 'logged out'

@app.route('/changepass_func', methods=['GET', 'POST'])
def changepass_func():
    if request.method == 'POST':
        if 'username' not in session:
            return '0'
        if len(request.data) > 0:
            data = dict([(s.split('=')[0],s.split('=')[1]) for s in request.data.split('&')])
        elif request.form.has_key('username'):
            data = request.form
        else:
            return '', 500
        username = session['username']
        old_pass = data['old_pass']
        new_pass = data['new_pass']
        new_pass_two = data['new_pass2']
        if not new_pass == new_pass_two:
            return '2'
        if check_pass(username, old_pass):
            sqlname = QuotedString(username).getquoted()
            sha = hashlib.sha512()
            sha.update(new_pass)
            hashword = QuotedString(sha.digest().encode('hex')).getquoted()
            cursor = connection.cursor()
            cursor.execute('update users set spassword={new_pass} where username={quoted_user};'.format(quoted_user=sqlname, new_pass=hashword))
            connection.commit()
            return '1'
        else:
            return '3'

def check_pass(username, password):
    sha = hashlib.sha512()
    sha.update(password)
    shashword = sha.digest().encode('hex')
    sha = hashlib.sha512()
    m = hashlib.md5()
    m.update(password)
    sha.update(m.digest().encode('hex'))
    mshashword = sha.digest().encode('hex')
    #hashword = m.digest().encode('hex')
    sqlname = QuotedString(username).getquoted()
    cursor = connection.cursor()
    cursor.execute('SELECT username, spassword from users where username={sqlname};'.format(sqlname=sqlname))
    a = cursor.fetchone()
    connection.commit()
    if a and (a[1] == shashword or a[1] == mshashword):
        return True
    else:
        return False


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if len(request.data) > 0:
            data = dict([(s.split('=')[0],s.split('=')[1]) for s in request.data.split('&')])
        elif request.form.has_key('username'):
            data = request.form
        else:
            return '', 500
        username = data['username']
        password = data['password']
        if check_pass(username, password):
            session['username'] = data['username']
            return '1'
        else:
            return '0'
        #return redirect(url_for('list_dir'))
    else:
        return '0'

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        if len(request.data) > 0:
            data = dict([(s.split('=')[0],s.split('=')[1]) for s in request.data.split('&')])
        elif request.form.has_key('username'):
            data = request.form
        else:
            return '', 500
        agreed = data['agreed']
        if not agreed:
            return '2'
        username = data['username']
        password = data['password']
        password2 = data['password2']
        if not password==password2:
            return '3'
        firstname = data['firstname']
        lastname = data['lastname']
        email = data['email'].replace('%40','@')
        org = data['organization']
        sha = hashlib.sha512()
        sha.update(password)
        hashword = QuotedString(sha.digest().encode('hex')).getquoted()
        sqlname = QuotedString(username).getquoted()
        sqlemail = QuotedString(email).getquoted()
        sqlorg = QuotedString(org).getquoted()
        sqlfirst = QuotedString(firstname).getquoted()
        sqllast = QuotedString(lastname).getquoted()
        d = datetime.datetime.now()
        timestamp = psycopg.Timestamp(d.year,d.month,d.day,d.hour,d.minute,d.second)
        cursor = connection.cursor()
        try:
            cursor.execute('INSERT INTO users(username,firstname,lastname,spassword,email,organization,registered_date,mou_agreed) VALUES({sqlname},{sqlfirst},{sqllast},{hashword},{email},{org},{registered_date},\'t\');'.format(sqlname=sqlname, hashword=hashword,email=sqlemail,org=sqlorg,registered_date=timestamp.getquoted(),sqlfirst=sqlfirst,sqllast=sqllast))
            connection.commit()
            session['username'] = data['username']
            return '1'
        except Exception, e:
            print e
            connection.rollback()
            return '0'
        #return redirect(url_for('list_dir'))
    else:
        return '0'

@app.route('/loginform')
def loginform():
    return render_template('loginform.html')

@app.route('/changepass')
def changepass():
    return render_template('change_pass.html')

@app.route('/changepass_form')
def changepass_form():
    return render_template('change_pass_form.html')

@app.route('/signupform')
def signupform():
    n = datetime.datetime.now()
    return render_template('signupform.html',day=ordinal_suffix(n.day),month=n.strftime('%B'))

@app.route('/interface')
def render_interface():
    if 'username' not in session:
        return redirect(url_for('list_dir'))
    return render_template('interface.html')

def date_handler(obj):
    return obj.strftime('%Y-%m-%dT%H:%M:%S') if type(obj) == datetime else obj

@app.route('/api', methods=['GET', 'POST'])
def get_candidates():
    if 'username' not in session:
        return redirect(url_for('list_dir'))
    #param_dict = defaultdict(lambda: None, request.args)
    query_fields = dict([(q, request.args[q]) for q in query_params if request.args.has_key(q) and request.args[q] != '' and '%' not in request.args[q]])
#    query_fields = [param_dict[q] for q in query_params if param_dict[q]]
    if len(query_fields) == 0:
        return 'Please provide some query parameters'
    print query_fields
    try:
        results = query_candidates(query_fields)
    except Exception, error:
        print error
    return json.dumps(results)

bip_query_params = {
        'candidate':('filed_mailing_address','election_key','name','phone','mailing_address','facebook_url','youtube','email','candidate_url','source','google_plus_url','twitter_name','incumbent','party','wiki_word','biography','photo_url','identifier','updated',),
        'contest':('number_voting_for','election_key','office','filing_closed_date','type','electoral_district_type','number_elected','custom_ballot_heading','contest_type','electorate_specifications','write_in','source','state','electoral_district_name','ballot_placement','partisan','primary_party','special','identifier','updated',),
        'electoral_district':('election_key','name','number','source','state_id','type','identifier','updated',),
        'referendum':("id","source","title","subtitle","brief","text","pro_statement","con_statement","contest_id","passage_threshold","effect_of_abstain","election_key","updated","identifier"),
        }

@app.route('/bip/<path:table>', methods=['GET', 'POST'])
def get_bip_table(table = ''):
    if 'username' not in session:
        return redirect(url_for('list_dir'))
    if table not in bip_query_params:
        return 'invalid table name'
    #param_dict = defaultdict(lambda: None, request.args)
    query_fields = dict([(q, request.args[q]) for q in bip_query_params[table] if request.args.has_key(q) and request.args[q] != '' and '%' not in request.args[q]])
#    query_fields = [param_dict[q] for q in query_params if param_dict[q]]
    if len(query_fields) == 0:
        return 'Please provide some query parameters'
    print query_fields
    try:
        results = query_bip(table,query_fields)
    except Exception, error:
        print error
    return json.dumps(results)

merged_query_params = ['{t}.{q}'.format(t=t,q=q) for t,v in bip_query_params.iteritems() for q in v]

@app.route('/bip/merged', methods=['GET', 'POST'])
def get_bip_merged_table(table = ''):
    if 'username' not in session:
        return redirect(url_for('list_dir'))
    #param_dict = defaultdict(lambda: None, request.args)
    query_fields = dict([(q, request.args[q]) for q in merged_query_params if request.args.has_key(q) and request.args[q] != '' and '%' not in request.args[q]])
#    query_fields = [param_dict[q] for q in query_params if param_dict[q]]
    if len(query_fields) == 0:
        return 'Please provide some query parameters'
    print query_fields
    try:
        results = query_merged_bip(query_fields)
    except Exception, error:
        print error
    return json.dumps(results)

def ordinal_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st","nd","rd"][day % 10 -1]
    return str(day)+suffix

words = gdbm.open('/home/gaertner/code/candidateview/words.db')
rhymes = gdbm.open('/home/gaertner/code/candidateview/rhymes.db')

def get_rhyme(word):
    word = word.upper()
    try:
        key, syllables = words[word].split()
    except:
        return word.lower()
    rhyme_words = [(rhyme,words[rhyme].split()[1]) for rhyme in rhymes[key].split()]
    rhyme_words = [rw[0] for rw in rhyme_words if rw[1] == syllables]
    if word in rhyme_words:
        rhyme_words.pop(rhyme_words.index(word))
    if len(rhyme_words) > 0:
        random.shuffle(rhyme_words)
        return rhyme_words[0].lower()
    return word.lower()

@app.route('/pun', methods=['GET','POST'])
def main():
    if request.method == 'POST':
        if len(request.data) > 0:
            data = dict([(s.split('=')[0],s.split('=')[1]) for s in request.data.split('&')])
        elif request.form.has_key('query'):
            data = request.form
        else:
            return 500
        query = data['query']
        r_query = []
        query = query.split()
        lq = len(query)
        num_rhymes = random.randint(1,lq)
        print num_rhymes
        idx = range(lq)
        random.shuffle(idx)
        for n in idx[:num_rhymes]:
            query[n] = get_rhyme(query[n])

        return redirect('https://www.google.com/search?q={query}'.format(query='+'.join(query)))
    else:
        return render_template('punsearch.html')

if __name__ == "__main__":
    app.run()
