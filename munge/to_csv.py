# Developed by: Will West
# 
# Utility functions used to convert data into CSVs easily readable in
# statistical packages like R and Matlab.

import json
import csv
import nltk
from nltk.corpus import cmudict

def pretty_print(obj):
	print json.dumps(obj, sort_keys=True, indent=4, separators=(',',': '))

def list_to_csv(l, filename):
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=l[0].keys())
		writer.writeheader()
		writer.writerows(l)


# Count syllables in a word.
#
# Doesn't use any fancy knowledge, just a few super simple rules:
# a vowel starts each syllable;
# a doubled vowel doesn't add an extra syllable;
# two or more different vowels together are a diphthong,
# and probably don't start a new syllable but might;
# y is considered a vowel when it follows a consonant.
#
# Even with these simple rules, it gets results far better
# than python-hyphenate with the libreoffice hyphenation dictionary.
#
# Copyright 2013 by Akkana Peck http://shallowsky.com.
# Share and enjoy under the terms of the GPLv2 or later.
def count_syllables(word, verbose=False):
    vowels = ['a', 'e', 'i', 'o', 'u']

    on_vowel = False
    in_diphthong = False
    minsyl = 0
    maxsyl = 0
    lastchar = None

    word = word.lower()
    for c in word:
        is_vowel = c in vowels

        if on_vowel == None:
            on_vowel = is_vowel

        # y is a special case
        if c == 'y':
            is_vowel = not on_vowel

        if is_vowel:
            if verbose: print c, "is a vowel"
            if not on_vowel:
                # We weren't on a vowel before.
                # Seeing a new vowel bumps the syllable count.
                if verbose: print "new syllable"
                minsyl += 1
                maxsyl += 1
            elif on_vowel and not in_diphthong and c != lastchar:
                # We were already in a vowel.
                # Don't increment anything except the max count,
                # and only do that once per diphthong.
                if verbose: print c, "is a diphthong"
                in_diphthong = True
                maxsyl += 1
        elif verbose: print "[consonant]"

        on_vowel = is_vowel
        lastchar = c

    # Some special cases:
    if word[-1] == 'e':
        minsyl -= 1
    # if it ended with a consonant followed by y, count that as a syllable.
    if word[-1] == 'y' and not on_vowel:
        maxsyl += 1

    return minsyl, maxsyl

def add_song_features(song):
	# Add song density by weighting the number of syllables in the song
	# against the duration of the track
	lyrics = song["lyrics"]
	lyrics = lyrics.replace('\n', ' ')

	words = lyrics.split()
	unique_words = list(set(words))

	num_syllables = count_syllables(lyrics)[0]
	song["syllable_count"] = num_syllables
	song["word_count"] = len(lyrics.split())
	song["song_density"] = num_syllables * 1.0 / song["spotify_duration"]
	song["song_unique_words"] = len(unique_words)
	song["song_word_count"] = len(words)
	song["song_diversity"] = song["song_unique_words"]*1.0 / song["song_word_count"]
	song["lyrics"] = song["lyrics"].replace('\n',' ')

def add_show_features(show):

	num_songs = 0
	lyrics = ""
	popularity = 0
	duration = 0

	for song in show["songs"]:
		if song["song_on_spotify"] == True and "has_lyrics" in song and song["has_lyrics"]=="true":
			num_songs+=1
			popularity += song["spotify_popularity"]
			add_song_features(song)
			lyrics = lyrics + " " + song["lyrics"].replace('\n', ' ')
			duration += song["spotify_duration"]


	lyrics = lyrics.lower()
	words = lyrics.split()
	unique_words = list(set(words))

	show["show_popularity"] = popularity*1.0 / num_songs
	show["num_unique_words"] = len(unique_words)
	show["show_lyrics"] = lyrics
	show["show_syllable_count"] = count_syllables(lyrics)[0]
	show["show_word_count"] = len(lyrics.split())
	show["album_duration"] = duration
	show["show_density"] = show["show_syllable_count"] * 1.0 / duration
	show["vocab_diversity"] = show["num_unique_words"]*1.0 / show["show_word_count"]


# Return a list (CSV) where each item (row) reperesents a song
def songs_csv(shows, export_file = None):
	results = []

	show_data = [
		"abstract",
		"book",
		"broadway",
		"id",
		# "lyrics",
		"music",
		# "name",
		"off_broadway",
		"on_dbpedia",
		"page_name",
		# "productions",
		"song_count",
		# "url",
		"wiki_name",
		"with_lyrics_count",
		"without_lyrics_count",
		"year",
		"num_unique_words",
		"vocab_diversity",
		"show_lyrics",
		"show_syllable_count",
		"show_word_count",
		"album_duration",
		"show_density",
		"show_popularity",
		"spotify_album_year"
	]

	song_data = [
		"has_lyrics",
		"lyrics",
		"spotify_duration",
		"spotify_popularity",
		"spotify_track_index",
		"spotify_track_name",
		"spotify_popularity",
		"song_density",
		"syllable_count",
		"word_count",
		"song_unique_words",
		"song_word_count",
		"song_diversity"
		# "name",
		# "url",
	]

	for show in shows:
		if show["without_lyrics_count"] == 0 and show["on_dbpedia"] == "true" and show["show_on_spotify"] == True:
			add_show_features(show)
			for song in show["songs"]:
				if song["song_on_spotify"] == True and "has_lyrics" in song and song["has_lyrics"]=="true":
					row = {}

					for key in show_data:
						if isinstance(show[key], basestring):
							row[key] = show[key].encode('ascii', 'ignore')
						else:
							row[key] = show[key]

					for key in song_data:
						if isinstance(song[key], basestring):
							row[key] = song[key].encode('ascii', 'ignore')
						else:
							row[key] = song[key]

					row["lyrics_by"] = show["lyrics"].encode('ascii', 'ignore')
					row["show_name"] = show["name"].encode('ascii', 'ignore')
					row["show_url"] = show["url"].encode('ascii', 'ignore')

					row["song_name"] = song["name"].encode('ascii', 'ignore')
					row["song_url"] = song["url"].encode('ascii', 'ignore')

					results.append(row)

	if export_file:
		list_to_csv(results, export_file)

	return results

# Return a list (CSV) where each item (row) reperesents a show
def shows_csv(shows, export_file = None):
	results = []

	show_data = [
		"abstract",
		"book",
		"broadway",
		"id",
		# "lyrics",
		"music",
		# "name",
		"off_broadway",
		"on_dbpedia",
		"page_name",
		# "productions",
		"song_count",
		# "url",
		"wiki_name",
		"with_lyrics_count",
		"without_lyrics_count",
		"year"
	]

	for show in shows:
		if show["without_lyrics_count"] == 0 and show["on_dbpedia"] == "true":
			row = {}

			for key in show_data:
				if isinstance(show[key], basestring):
					row[key] = show[key].encode('ascii', 'ignore')
				else:
					row[key] = show[key]

			row["lyrics_by"] = show["lyrics"].encode('ascii', 'ignore')
			row["show_name"] = show["name"].encode('ascii', 'ignore')
			row["show_url"] = show["url"].encode('ascii', 'ignore')

			results.append(row)

	if export_file:
		list_to_csv(results, export_file)

	return results


with open("../data/shows_w_spotify.json", 'r') as f:
	shows = json.load(f)

songs_csv(shows, export_file="../data/songs.csv")

# shows_csv(shows, export_file="../data/shows.csv")