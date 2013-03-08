candidate_api
This swell little guy runs a Flask app as a wsgi module to control access to and facilitate queries on the Ballot Information Project candidate data.
It uses the Flask AutoIndex plugin (http://packages.python.org/Flask-AutoIndex/) to generate directory listings for the raw candidate data files.
It provides some API functionality for querying the various datasets, documented here: https://ballotinfo.org/api_user_guide.html
There's even a nice little interface here: https://ballotinfo.org/list/interface (you'll have to sign up to use it though. Sign up here: https://ballotinfo.org/list)
This runs at https://ballotinfo.org/
The API is just Flask serving up JSON dumps of the PostgreSQL database's response to queries.
The interface is built on top of AJAX calls that use the API. The table in it uses this jQuery plugin: http://tablesorter.com/docs/
The javascript that does the AJAX calls is here: https://github.com/natgaertner/candidate_api/blob/master/static/js/login.js
