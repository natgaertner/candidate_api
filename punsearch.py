from flask import Flask
import json, os, re, hashlib,datetime
from collections import defaultdict
from flask import request, session, redirect,url_for, render_template
import random
import gdbm
app = Flask(__name__)
app.secret_key = '\xe9\x83\x88v\x97\x16\xe1\x06r\xa3+\xd0W\xfb\xea\xa4L\x06LW\xe0\xca\xff\x8a'
words = gdbm.open('words.db')
rhymes = gdbm.open('rhymes.db')

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

@app.route('/', methods=['GET','POST'])
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
        return render_template('index_template.html')

if __name__ == "__main__":
    app.run()
