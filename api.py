# Search Engine REST API 2020.08.13
# Author: Zoltan Peter Tokos
# Email: zoltan.p.t@gmail.com

import flask
import os, os.path
import ntpath

from flask import request, jsonify

from whoosh import index, scoring
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import QueryParser
from whoosh.analysis import SimpleAnalyzer, CharsetFilter, KeywordAnalyzer
#from whoosh.support.charset import accent_map

# ===== GLOBAL VARIABLES ========

file_dir = "files"
index_dir = "index"
response = []
schema_name = "search"
schema = Schema(path=ID(unique=True, stored=True), time=STORED, content=TEXT(analyzer=KeywordAnalyzer()))

#my_analyzer = SimpleAnalyzer() | CharsetFilter(accent_map)
#schema_fuzzy = Schema(path=ID(unique=True, stored=True), time=STORED, content=TEXT(analyzer=my_analyzer))

# ========= REST API =============
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Home
@app.route('/', methods=['GET'])
def home():
	return "<h1>Home</h1><p>Try to pass search terms with: http://127.0.0.1:5000/search?q=comma,separated,search,terms</p>"

# Search engine
@app.route('/search', methods=['GET'])
def api_search():
	return main(request.args)


# ================ FUNCTIONS =================
# Main
def main(terms):
	# create the files directory if not exists
	if not os.path.exists(file_dir):
		os.mkdir(file_dir)

	if 'q' in terms:
		terms_list = terms['q'].split(',')
		
		ix = init_index(schema, schema_name)		

		custom_weighting = scoring.FunctionWeighting(custom_score)
		with ix.searcher(weighting=custom_weighting) as searcher:
			for term in terms_list:
				results = search_term(term, schema, ix, searcher)

				if results:
					for r in results:
						result={}
						result['path'] = ntpath.basename(dict(r)['path'])
						result['score']	= r.score
						response.append({'path': result['path'], 'score' : result['score'] })
	else:
		return "Error: No search terms provided. Please specify search terms."
	return jsonify(response)


# Function: Creates and fills the indexes
def init_index(search_schema, index_name):
	# Create or clear index
	index.create_in(index_dir, search_schema, indexname=index_name)
	# Indexing files
	ix = index.open_dir(index_dir, indexname=index_name)

	writer = ix.writer()
	for filename in os.listdir(file_dir):
		filepath = file_dir + '/' + filename
		if os.path.isfile(filepath):
			add_doc(writer, filepath)
	writer.commit(optimize=True)
	return ix

# Function: Document indexing
def add_doc(writer, path):
	fileobj = open(path, "rb")
	content = fileobj.read()
	fileobj.close()
	modtime = os.path.getmtime(path)
	writer.add_document(path=str(path), content=str(content), time=modtime)

def search_term(term, schema, ix, searcher):
	query = QueryParser("content", schema=ix.schema).parse(str(term))
	return searcher.search(query, terms=True, limit=None)


# Function: Customize scoring.py
def custom_score(searcher, fieldname, text, matcher):
	if int(matcher.weight()) > 1:
		return 1.0
	if int(matcher.block_max_weight()) > 1:
		return 1.0

	return matcher.weight()

app.run()
