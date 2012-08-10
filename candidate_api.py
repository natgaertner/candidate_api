from flask import Flask
import json
from collections import defaultdict
from flask import request
from sql_utils import query_candidates
app = Flask(__name__)

query_params = ['state','office_level','electoral_district','office_name','candidate_name','candidate_party']

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/candidates', methods=['GET'])
def get_candidates():
    #param_dict = defaultdict(lambda: None, request.args)
    query_fields = [(q, request.args[q]) for q in query_params if request.args.has_key(q) and request.args[q] != '' and '%' not in request.args[q]]
#    query_fields = [param_dict[q] for q in query_params if param_dict[q]]
    if len(query_fields) == 0:
        return 'Please provide some query parameters'
    print query_fields
    try:
        results = query_candidates(query_fields)
    except Exception, error:
        print error
    return json.dumps(results)
#return str(query_fields)

@app.route('/reload', methods=['POST'])
def reload_candidates():
    return 'hi!'

if __name__ == "__main__":
    app.run()
