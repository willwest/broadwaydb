# Developed by: Will West
# 
# Utility functions used to convert data into CSVs easily readable in
# statistical packages like R and Matlab.

import json
import csv


def list_to_csv(l, filename):
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=l[0].keys())
		writer.writeheader()
		writer.writerows(l)

# Return a list (CSV) where each item (row) reperesents a song
def songs_csv(shows, export_file = None):
	results = []

	show_data = [
		"abstract",
		"book",
		"broadway",
		"id",
		"lyrics",
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

	song_data = [
		"has_lyrics",
		"lyrics",
		# "name",
		# "url",
	]

	for show in shows:
		if show["without_lyrics_count"] == 0 and show["on_dbpedia"] == "true":
			for song in show["songs"]:
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
		"lyrics",
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

			row["show_name"] = show["name"].encode('ascii', 'ignore')
			row["show_url"] = show["url"].encode('ascii', 'ignore')

			results.append(row)

	if export_file:
		list_to_csv(results, export_file)

	return results


with open("../data/shows_combined.json.matched", 'r') as f:
	shows = json.load(f)

songs_csv(shows, export_file="../data/songs.csv")

shows_csv(shows, export_file="../data/shows.csv")