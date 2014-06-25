import json
import urllib3
import time
from pyechonest import artist
from pyechonest import song
from pyechonest import config
import api_keys

# Get secret keys
KEYS = api_keys.get_keys()

config.ECHO_NEST_API_KEY= KEYS["ECHO_NEST_API_KEY"]

def request_track(spotify_id):
	bucket = "audio_summary"

	uri = ("http://developer.echonest.com/api/v4/track/"
			"profile?"
			"api_key=" + KEYS["ECHO_NEST_API_KEY"] +
			"&id=" + spotify_id +
			"&bucket=" + bucket + 
			"&format=json" )

	try:
		response = make_request(uri)
	except StandardError:
		raise StandardError()

	return response["response"]["track"]["audio_summary"]
	

# Given a url, make a GET request with exponential backoff
def make_request(url):
	http = urllib3.PoolManager()

	min_remaining = 5
	backoff = 5

	while True:	
		try:
			r = http.request('GET', url, timeout=urllib3.Timeout(total=5.0))
			response = json.loads(r.data)
			if r.status != 200:
				# If request failed due to rate limiting, sleep for a minute
				# and then try again.
				if r.status == 429:
					print ("\tFailed due to rate limit."
						   "Sleeping for 65 seconds...")
					time.sleep(65)
					continue

				raise IOError("\tError: couldn't crawl " + url)

			# If the song is not on Echonest
			if response["response"]["status"]["code"] == 5:
				print "\tError: Song not found"
				raise StandardError()

			# If there are less than min_remaining requests, sleep for one
			# minute before returning data
			if int(r.headers["x-ratelimit-remaining"]) < min_remaining:
				print "\tAbout to hit rate limit. Sleeping for 65 seconds..."
				time.sleep(65)
			
			return response

		# If we time out, perform backoff (increasing exponentially)
		except urllib3.exceptions.TimeoutError:
			print "\tError: timed out on url: " + url
			print "\tSleeping for " + str(backoff) + " seconds..."

		# Exponential backoff
		backoff = 2 ** backoff
		time.sleep(backoff)


with open('../data/shows_w_spotify.json', 'r') as f:
	data = json.load(f)

for show in data:
	if show["show_on_spotify"]:
		print "Show: {}".format(show["name"])
		for song_obj in show["songs"]:
			if song_obj["song_on_spotify"]:
				print "\tSong: {}".format(song_obj["spotify_track_name"].encode('ascii', 'ignore'))
				try:
					audio_summary = request_track(song_obj["spotify_track"])
					song_obj["on_echonest"] = True
					song_obj["audio_summary"] = audio_summary
				except StandardError:
					song_obj["on_echonest"] = False
			else:
				song_obj["on_echonest"] = False

with open('../data/songs_w_echonest.json', 'w') as f:
	json.dump(data, f)
