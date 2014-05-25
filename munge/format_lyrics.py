import json

def format_lyrics(lyrics):
	lyrics = lyrics.strip().replace('\r','').split('\n')

	formatted = []

	# iterate over copy of list
	for lyric in lyrics[:]:
		if lyric == '':
			lyrics.remove(lyric)
			continue

		if lyric[-1] == ':':
			lyrics.remove(lyric)
			continue

		if lyric[-1] == ']':
			lyrics.remove(lyric)
			continue

		if lyric.isupper():
			lyrics.remove(lyric)
			continue

		# Check word by word...
		words = lyric.split(' ')

		for word in words[:]:
			if word.strip() == '':
				words.remove(word)
			
			elif word[-1] == ':' and word[:-1].isupper():
				words.remove(word)

			elif word.lower() == '(spoken)' or word.lower() == '(sung)':
				words.remove(word)

			word = word.strip()

		formatted.append(' '.join(words))

	return '\n'.join(formatted)



with open("../data/shows_w_songs_w_lyrics.json", 'r') as f:
	data = json.load(f)

for show in data:
	for song in show["songs"]:
		if "lyrics" in song:
			song["lyrics"] = format_lyrics(song["lyrics"])
			song["lyrics"] = format_lyrics(song["lyrics"])
			song["lyrics"] = song["lyrics"].encode('ascii', 'ignore')

with open("../data/shows_w_songs_w_lyrics.json.formatted", 'w') as outfile:
	json.dump(data, outfile)
