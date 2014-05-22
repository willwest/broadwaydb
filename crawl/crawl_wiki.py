import urllib3
import json
import time
import re

# return list of pages in a given category
# Note: category should contain "Category:" prefix
def in_category(category, template_only=False, page_only=False, import_file=None):
	if import_file:
		with open(import_file, 'r') as f:
			pages = [line.strip() for line in f]
			return pages

	s = "http://en.wikipedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle="+category+"&cmlimit=max"

	http = urllib3.PoolManager()

	response = http.request('GET', s)
	response = json.loads(response.data)

	# get all page titles from response
	pages = [page["title"] for page in response["query"]["categorymembers"]]

	while "query-continue" in response.keys():
		s = "http://en.wikipedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle="+category+"&cmlimit=max&cmcontinue="+response["query-continue"]["categorymembers"]["cmcontinue"]

		response = http.request('GET', s)
		response = json.loads(response.data)

		# get all page titles from response
		pages = pages +  [page["title"] for page in response["query"]["categorymembers"]]

	if template_only:
		pages = [page for page in pages if "Template:" in page]

	if page_only:
		pages = [page for page in pages if "Template:" not in page and "Category:" not in page]

	pages = [page.encode('ascii', 'ignore') for page in pages]

	with open('../data/show_list' ,'w') as outfile:
		outfile.write('\n'.join(pages))
		outfile.write('\n')

	return pages

def format_page(page):
	page = page.split('/')[-1]
	page = page.replace('_', ' ')
	page = re.sub(r'\([^)]*\)', '', page)

	return page

def get_infobox_data(page):
	show = {}
	base = "http://dbpedia.org/data/"
	page = page.replace(' ', '_')
	uri = base + page + ".json"

	http = urllib3.PoolManager()

	print uri

	backoff = 2
	while True:
		try:
			response = http.request('GET', uri, timeout=urllib3.Timeout(total=5.0))
			break
		except urllib3.exceptions.TimeoutError:
			print "Error: timed out on url: " + uri
			print "Sleeping for " + str(backoff) + " seconds..."

			time.sleep(backoff)
			backoff = backoff ** 2

	response = json.loads(response.data)
	
	primary_key = [{'key':key, 'length':len(response[key].keys())} for key in response.keys()]

	max_len = -1

	for key in primary_key:
		if key['length'] > max_len:
			max_len = key['length']
			good_key = key['key']


	response = response[good_key]	

	# Name
	show["name"] = response["http://xmlns.com/foaf/0.1/name"][0]["value"]
	# show["comment"] = response["http://www.w3.org/2000/01/rdf-schema#comment"][0]["value"]
	
	# Productions
	if "http://dbpedia.org/property/productions" in response:
		show["productions"] = [production["value"] for production in response["http://dbpedia.org/property/productions"] if len(str(production["value"]))==4]

	# Abstract
	if "http://dbpedia.org/ontology/abstract" in response:
		show["abstract"] = response["http://dbpedia.org/ontology/abstract"][0]["value"]

	# Music By
	if "http://dbpedia.org/property/music" in response:
		show["music"] = format_page(response["http://dbpedia.org/property/music"][0]["value"])
	
	elif "http://dbpedia.org/ontology/musicBy" in response:
		show["music"] = format_page(response["http://dbpedia.org/ontology/musicBy"][0]["value"])

	# Lyrics
	if "http://dbpedia.org/property/lyrics" in response:
		show["lyrics"] = format_page(response["http://dbpedia.org/property/lyrics"][0]["value"])

	# Book
	if "http://dbpedia.org/property/book" in response:
		show["book"] = format_page(response["http://dbpedia.org/property/book"][0]["value"])

	return show


pages = in_category(import_file = "../data/show_list", category="Category:Broadway_musicals", page_only=True)

pages = [get_infobox_data(page) for page in pages]

with open('../data/wiki_data', 'w') as outfile:
	json.dump(pages, outfile)
	
