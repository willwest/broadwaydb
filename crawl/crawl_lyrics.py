import bs4
import urllib3
import string
import sys
import json
import time

# returns list of letters from a to z
def a_to_z(upper=False, incl_hash=False):
	letters = list(string.lowercase[:26])

	if incl_hash==True:
		letters.append('19')

	return letters


# Given a url, make a GET request with exponential backoff
def make_request(url):
	http = urllib3.PoolManager()

	backoff = 5
	while True:	
		try:
			r = http.request('GET', url, timeout=urllib3.Timeout(total=5.0))
			if r.status != 200:
				raise IOError("Error: couldn't crawl " + url)
			return r.data
		except urllib3.exceptions.TimeoutError:
			print "Error: timed out on url: " + url
			print "Sleeping for " + str(backoff) + " seconds..."

		# exponential backoff
		backoff = 2 ** backoff
		time.sleep(backoff)

# returns a dict of shows
def get_shows(import_file = None):

	# if given a filename to import, don't crawl
	if import_file:
		with open(import_file, 'r') as f:
			data = json.loads(f.read())
			return data

	base = "http://www.allmusicals.com/"
	shows = []

	for letter in a_to_z(incl_hash=True):
		url = base + letter + ".htm"
		print url
		
		try:
			html_doc = make_request(url)
		except:
			continue

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

	
# given a list of shows, returns an updated list of songs/shows
def add_songs(shows):
	for show in shows:
		url = show['url']

		print "crawling " + url

		try:
			html_doc = make_request(url)
		except:
			continue

		soup = bs4.BeautifulSoup(html_doc)

		song_list = soup.find_all('ol', class_="st-list")

		if len(song_list) != 1:
			print "CSS Parse Error: returned show_list length != 1 for url: "+url

		song_list = song_list[0].find_all('li')
		
		show['songs'] = []

		for song in song_list:
			grey = song.find_all('span', class_="grey")

			# if the song has no lyrics
			if grey:
				has_lyrics = "false"
				url = "null"
				name = grey[0].contents[0]

				if name.strip() not in ["Act 1", "Act 2", "Act 3", "BONUS TRACKS", "Act 1:", "Act 2:", "Act 3:", "Act I", "Act II", "Act III"]:
					show['songs'].append({'url':url, 'name':name, 'has_lyrics':has_lyrics})

			else:
				a = song.find_all('a')

				url = a[0]['href']
				name = a[0].contents[0]
				has_lyrics = "true"

				show['songs'].append({'url':url, 'name':name, 'has_lyrics':has_lyrics})

		show['song_count'] = len(show['songs'])


	with open('../data/shows_w_songs.json', 'w') as outfile:
		json.dump(shows, outfile)


def add_lyrics(shows):
	for show in shows:
		for song in show["songs"]:
			if song["has_lyrics"] == "true":
				try:
					print "Crawling " + song["url"]
					html_doc = make_request(song["url"])
					soup = bs4.BeautifulSoup(html_doc)
					soup = soup.find_all(id='page')

					if len(soup) < 1:
						print "Error: no lyrics found"
						song["has_lyrics"] = "false"
						continue

					# Remove invisible title
					soup[0].h2.extract()

					# Extract text
					lyrics = soup[0].get_text().strip()

					song["lyrics"] = lyrics

				except IOError:
					continue

	with open('../data/shows_w_songs_w_lyrics.json', 'w') as outfile:
		json.dump(shows, outfile)

	return shows

shows = get_shows(import_file="../data/shows_w_songs.json")

# add_songs(shows)
add_lyrics(shows)
