import bs4
import urllib3
import string
import sys
import json

# returns list of letters from a to z
def a_to_z(upper=False, incl_hash=False):
	letters = list(string.lowercase[:26])

	if incl_hash==True:
		letters.append('19')

	return letters


# returns a dict of shows
def get_shows(import_file = None):

	# if given a filename to import, don't crawl
	if import_file:
		with open(import_file, 'r') as f:
			data = json.loads(f.read())
			return data

	base = "http://www.allmusicals.com/"
	http = urllib3.PoolManager()
	shows = []

	for letter in a_to_z(incl_hash=True):
		url = base + letter + ".htm"
		print url
		r = http.request('GET', url)

		# if url is not valid
		if r.status != 200:
			print "Error: couldn't crawl " + url
			sys.exit()

		html_doc =  r.data
		soup = bs4.BeautifulSoup(html_doc)
		show_list = soup.find_all("ul", class_="symz")

		# if we found more than one ul with class name symz, exit
		if len(show_list) != 1:
			print "CSS Parse Error: returned show_list length != 1"
			sys.exit()

		# extract each link object from the ul
		show_list = show_list[0].find_all('a')

		for show in show_list:
			contents = show.contents[0]
			url = show['href']
			name = contents[:-14] # remove 'Lyrics' and year
			year = contents[-4:]

			shows.append({'name':name, 'url':url, 'year':year})


	with open('../data/shows.json', 'w') as outfile:
		json.dump(shows, outfile)

	return shows

	
# given a list of shows, returns a list of songs/shows
def get_songs(shows):
	for show in shows:
		print show


shows = get_shows()
get_songs(shows)

