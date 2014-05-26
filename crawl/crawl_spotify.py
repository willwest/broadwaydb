import spotify
import threading
import json
import nltk.metrics.agreement
import api_keys

# Get secret keys
KEYS = api_keys.get_keys()

logged_in_event = threading.Event()

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

# Given a target string and a list of candidate strings, return the best 
# matching candidate
def match(target, candidate_list, distance_only=False):
	distances = []

	for item in candidate_list:
		dist = nltk.metrics.edit_distance(target, item)*1.0 / len(target)
		distances.append(dist)

	if distance_only:
		return min(distances)

	# Get index of minimum distance
	return distances.index(min(distances))

def search_score(target_tracks, matching_tracks):
	distances = []

	for target in target_tracks:
		dist = match(target, matching_tracks, distance_only=True)
		distances.append(dist)

	return (sum(distances) / len(distances)) + abs(len(target_tracks)-
		len(matching_tracks))/len(distances)

def search_for_album(query):
	scores = []

	print 'Searching for "{}"'.format(query)

	search = session.search(query)

	# Assume that the first search result is the best. Should change this
	# to a better method.
	search = search.load()
	album_results = search.albums

	if len(album_results) == 0:
		raise StandardError("Error: no search results found.")

	for album in album_results:
		album.load()

		# Obtain track list
		browser = album.browse().load()
		tracks = browser.tracks

		track_names = [track.name for track in tracks]
		target_names = [song["name"] for song in show["songs"]]
		
		score = search_score(target_names, track_names)
		scores.append(score)

	if min(scores) > .3:
		raise StandardError("Error: no results above threshold")

	return album_results[scores.index(min(scores))]

with open('../data/shows_combined.json.matched', 'r') as f:
	data = json.load(f)

for show in data:
	show_name = show["name"]
	
	print show_name

	try:
		album = search_for_album(show_name)
	except StandardError as e:
		print e
		continue

	album.load()
	browser = album.browse().load()
	tracks = browser.tracks
	track_names = [track.name for track in tracks]

	for song in show["songs"]:
		track_index = match(song["name"], track_names)
		track = tracks[track_index]
		print '"{}", "{}"'.format(
			song["name"].encode('ascii','ignore'), track.name)
	# cover_art_file = '../data/cover_art/'+str(album.link)+'.jpg'
	# open(cover_art_file,'w+').write(album.cover().load().data)

	# # Record album-specific data
	# show["spotify_album"] = str(album.link)
	# show["album_year"] = album.year
	# show["album_artist"] = album.artist.name
	# show["cover_art"] = cover_art_file

	# for song in show["songs"]:
	# 	track_index = match(song["name"], track_names)
	# 	track = tracks[track_index]

	# 	song["popularity"] = track.popularity
	# 	song["duration"] = track.duration / 1000
	# 	song["spotify_track"] = str(track.link)
	# 	song["spotify_artists"] = [str(artist.link) for artist in track.artists]
	# 	song["track_index"] = track.index
	# 	print song
	# print album




