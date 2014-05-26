import json
from pyechonest import artist
from pyechonest import song
from pyechonest import config
import api_keys

# Get secret keys
KEYS = api_keys.get_keys()

config.ECHO_NEST_API_KEY= KEYS["ECHO_NEST_API_KEY"]

with open('../data/shows_combined.json.matched', 'r') as f:
	data = json.load(f)

for show in data:
	if show["name"] == "Next to Normal":
		for song_obj in show["songs"]:
			song_result = song.search(title=song_obj["name"], style="soundtrack")
			print song_obj["name"], song_result
			for result in song_result:
				print result
				print result.get_song_type()
			break

