import urllib3
import json
import time
import re

# return list of pages in a given category
# Note: category should contain "Category:" prefix
def in_category(category, template_only=False, page_only=False, import_file=None, export_file=None):
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

	if export_file:
		with open(export_file ,'w') as outfile:
			outfile.write('\n'.join(pages))
			outfile.write('\n')

	return pages

def format_url(page):
	page = page.split('/')[-1]
	page = page.replace('_', ' ')
	page = page.replace('(musical)', '')
	page = page.replace('(Musical)', '')
	page = page.replace('(opera)', '')
	page = page.replace('(Opera)', '')
	page = page.strip()

	return page

def format_page(page):
	page = page.replace('_', ' ')
	page = page.replace('(musical)', '')
	page = page.replace('(Musical)', '')
	page = page.replace('(opera)', '')
	page = page.replace('(Opera)', '')
	page = page.strip()

	return page

def get_infobox_data(page, broadway_pages, off_broadway_pages):
	show = {}
	base = "http://dbpedia.org/data/"

	if page in off_broadway_pages:
		off_broadway = 'true'
	else:
		off_broadway = 'false'

	if page in broadway_pages:
		broadway = 'true'
	else:
		broadway = 'false'

	page = page.replace(' ', '_')
	uri = base + page + ".json"

	http = urllib3.PoolManager()

	print uri

	retries = 0

	while True:
		try:
			response = http.request('GET', uri, timeout=urllib3.Timeout(total=5.0))
			break
		except urllib3.exceptions.TimeoutError:
			print "Error: timed out on url: " + uri

			retries += 1
			backoff = 2 ** retries

			print "Sleeping for " + str(backoff) + " seconds..."

			time.sleep(backoff)

	response = json.loads(response.data)

	if not response:
		print "Error: no data found"
		show = {'page_name':page, 'on_dbpedia':'false', 'name':format_page(page), 'productions':[], 'abstract':'null', 'music':'null', 'lyrics':'null', 'book':'null', 'off_broadway':off_broadway, 'broadway':broadway}
		return show

	primary_key = [{'key':key, 'length':len(response[key].keys())} for key in response.keys()]

	max_len = -1

	for key in primary_key:
		if key['length'] > max_len:
			max_len = key['length']
			good_key = key['key']


	response = response[good_key]

	show["on_dbpedia"] = 'true'

	show["page_name"] = page

	show["broadway"] = broadway
	show["off_broadway"] = off_broadway

	show["name"] = format_page(page)
	
	# Productions
	if "http://dbpedia.org/property/productions" in response:
		show["productions"] = [production["value"] for production in response["http://dbpedia.org/property/productions"] if len(str(production["value"]))==4]
	else:
		show["productions"] = []

	# Abstract
	if "http://dbpedia.org/ontology/abstract" in response:
		show["abstract"] = response["http://dbpedia.org/ontology/abstract"][0]["value"]
	else:
		show["abstract"] = "null"

	# Music By
	if "http://dbpedia.org/property/music" in response:
		show["music"] = format_url(response["http://dbpedia.org/property/music"][0]["value"])
	elif "http://dbpedia.org/ontology/musicBy" in response:
		show["music"] = format_url(response["http://dbpedia.org/ontology/musicBy"][0]["value"])
	else:
		show["music"] = "null"

	# Lyrics
	if "http://dbpedia.org/property/lyrics" in response:
		show["lyrics"] = format_url(response["http://dbpedia.org/property/lyrics"][0]["value"])
	else:
		show["lyrics"] = "null"

	# Book
	if "http://dbpedia.org/property/book" in response:
		show["book"] = format_url(response["http://dbpedia.org/property/book"][0]["value"])
	else:
		show["book"] = "null"

	return show


broadway_pages = in_category(export_file = "../data/broadway_shows", category="Category:Broadway_musicals", page_only=True)

off_broadway_pages = in_category(export_file = "../data/off_broadway_shows", category="Category:Off-Broadway_musicals", page_only=True)

# get all unique pages from both sets
all_pages = list(set(broadway_pages + off_broadway_pages))
all_pages.sort()

# write all pages to file
with open("../data/all_shows" ,'w') as outfile:
	outfile.write('\n'.join(all_pages))
	outfile.write('\n')

# get data for each page
all_pages = [get_infobox_data(page, broadway_pages, off_broadway_pages) for page in all_pages]

with open('../data/wiki_data', 'w') as outfile:
	json.dump(all_pages, outfile)

