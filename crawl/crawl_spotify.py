import spotify
import threading
import json
import os
import nltk.metrics.agreement
import api_keys

# Get secret keys
KEYS = api_keys.get_keys()

logged_in_event = threading.Event()

def pretty_print(obj):
	print json.dumps(obj, sort_keys=True, indent=4, separators=(',',': '))

def connection_state_listener(session):
	if session.connection.state is spotify.ConnectionState.LOGGED_IN:
		logged_in_event.set()

# Specify configuration
config = spotify.Config()
config.user_agent = 'My awesome Spotify client'
config.tracefile = b'/tmp/libspotify-trace.log'

print "Opening session with user {}...".format(KEYS["SPOTIFY_USERNAME"])
# Open session and loop
session = spotify.Session(config)
loop = spotify.EventLoop(session)
loop.start()
session.on(
	spotify.SessionEvent.CONNECTION_STATE_UPDATED,
	connection_state_listener)
session.login(KEYS["SPOTIFY_USERNAME"],KEYS["SPOTIFY_PASSWORD"])
logged_in_event.wait()

print "Logged in and waiting..."

# Return the greatest common suffix in a list of strings
def greatest_common_suffix(list_of_strings):
	reversed_strings = [' '.join(s.split()[::-1]) for s in list_of_strings]
	reversed_gcs = os.path.commonprefix(reversed_strings)
	gcs = ' '.join(reversed_gcs.split()[::-1])
	return gcs


def score(target, item):
	target = target.lower()
	item = item.lower()

	return nltk.metrics.edit_distance(target, item)*1.0 / len(target)

def match(target, candidate_list, distance_only=False):
	""" Given a target string and a list of candidate strings, return the best 
	matching candidate.
	"""
	distances = []

	for item in candidate_list:
		dist = score(target, item)
		distances.append(dist)

	if distance_only:
		return min(distances)

	# Get index of minimum distance
	return distances.index(min(distances))

def search_score(target_tracks, matching_tracks):
	""" Given a list of track names to be matched, and a list of matching
	tracks, returns a score that approximates the confidence that the match
	is valid.

	The score is based on the average of the edit distance between each target
	track and its best match, offset by the difference in the length of each
	list.
	"""
	distances = []

	for target in target_tracks:
		dist = match(target, matching_tracks, distance_only=True)
		distances.append(dist)

	return (sum(distances) / len(distances)) + abs(len(target_tracks)-
		len(matching_tracks))/len(distances)

def search_for_album(show):
	query = show["name"]
	search = session.search(query)

	# Execute search query
	search = search.load()
	album_results = search.albums

	print '\nSearching for "{}"'.format(query)

	# If we find no results, report error
	if len(album_results) == 0:
		raise StandardError("Error: no search results found.")

	scores = []

	for album in album_results:
		album.load()

		# Obtain track list
		browser = album.browse().load()
		tracks = browser.tracks

		# Get lists of candidate album's track names and
		# the actual track names
		track_names = [clean_track_name(track.name, album, browser) for track in tracks]
		target_names = [song["name"] for song in show["songs"]]
		
		# Obtain a similarity score between the two lists
		score = search_score(target_names, track_names)

		# Save the score
		scores.append(score)

	# If none of the results have an acceptable score, report
	# an error
	if min(scores) > .3:
		raise StandardError("Error: no results above threshold")

	return album_results[scores.index(min(scores))]

def ascii(s):
	return s.encode('ascii', 'ignore')

def add_spotify_song_data(song, spotify_track):
	song["spotify_popularity"] = spotify_track.popularity
	song["spotify_duration"] = spotify_track.duration / 1000
	song["spotify_track"] = str(spotify_track.link)
	song["spotify_track_name"] = spotify_track.name
	song["spotify_match_score"] = match_score

	artists= [str(artist.link) for artist in spotify_track.artists]
	artist_names = [ascii(artist.name) for artist in spotify_track.artists]
	song["spotify_artists"] = artists
	song["spotify_artist_names"] = artist_names

	song["spotify_track_index"] = spotify_track.index

def add_spotify_album_data(album, spotify_album):
	# Save the cover art file found on Spotify
	cover_art_file = '../data/cover_art/'+str(spotify_album.link)+'.jpg'
	open(cover_art_file,'w+').write(spotify_album.cover().load().data)

	# Record album-specific data
	show["show_on_spotify"] = True
	show["spotify_album"] = str(spotify_album.link)
	show["spotify_album_year"] = spotify_album.year
	show["spotify_album_artist"] = ascii(spotify_album.artist.name)
	show["spotify_cover_art"] = cover_art_file


def clean_track_name(track_name, album, browser):
	browser = album.browse().load()
	tracks = browser.tracks
	track_names = [track.name for track in tracks]

	gcs = greatest_common_suffix(track_names)

	track_name = ascii(track_name).lower()
	album_name = ascii(album.name).lower().replace(' the musical','')

	# Remove greatest common suffix if large enough
	if len(gcs) > 3:
		track_name = track_name.replace(gcs.lower(), '')

	# Remove "(From "[show_name]")" from track name if present
	track_name = track_name.replace('(from "{}")'.format(album_name),'')

	# Remove "- Musical "[show_name]"" from track name if present
	track_name = track_name.replace(' - musical "{}"'.format(album_name),'')

	# Remove " - feat.*" if present
	track_name = track_name.split(" - feat. ")[0]

	return track_name


with open('../data/shows_combined.json.matched', 'r') as f:
	data = json.load(f)

for show in data:
	show_name = show["name"]

	# Try to search Spotify for the album. If no suitable matches are found,
	# note that the album was not found on Spotify and move on.
	try:
		album = search_for_album(show)
	except StandardError as e:
		show["show_on_spotify"] = False
		print e
		continue

	# Load the album, get the track list, and produce a list of track names
	# on the Spotify album
	album.load()
	browser = album.browse().load()
	tracks = browser.tracks
	track_names = [clean_track_name(track.name, album, browser) for track in tracks]

	show["spotify_song_count"] = len(track_names)

	add_spotify_album_data(show, album)

	# Keep track of any songs that we find on spotify that we didn't have
	# saved before
	new_songs = []

	# For each song in the show, find a match from the track list. 
	for song in show["songs"]:
		track_index = match(song["name"], track_names)
		matching_track = tracks[track_index]
		matching_track_name = clean_track_name(matching_track.name, album, browser)

		song_name = ascii(song["name"])

		match_score = score(song_name,matching_track_name)

		print '\t"{}", "{}": {}'.format(
			song_name, matching_track_name, match_score)

		if match_score < .7:
			song["song_on_allmusicals"] = True
			song["song_on_spotify"] = True

			add_spotify_song_data(song, matching_track)
			
		else:
			new_song = {}
			song["song_on_spotify"] = False
			song["song_on_allmusicals"] = True

			new_song["song_on_spotify"] = True
			new_song["song_on_allmusicals"] = False

			add_spotify_song_data(new_song, matching_track)

			collected = [s["spotify_track"] for s in new_songs]
			
			if new_song["spotify_track"] not in collected:
				new_songs.append(new_song)

	collected = [s["spotify_track"] for s in show["songs"] 
					if "spotify_track" in s]
	new_songs = [s for s in new_songs if s["spotify_track"] not in collected]

	show["songs"].extend(new_songs)


with open('../data/shows_w_spotify.json', 'w') as outfile:
	json.dump(data, outfile)

