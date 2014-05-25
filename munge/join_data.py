import json
import string
import nltk.metrics.agreement

def format_show_name(name):
	num_dict = {
		"0": 'zero',
		"1": 'one',
		"2": 'two',
		"3": 'three',
		"4": 'four',
		"5": 'five',
		"6": 'six',
		"7": 'seven',
		"8": 'eight',
		"9": 'nine',
		"10": 'ten',
		"11": 'eleven',
		"12": 'twelve',
		"13": 'thirteen',
		"14": 'fourteen',
		"15": 'fifteen',
		"16": 'sixteen',
		"17": 'seventeen',
		"18": 'eighteen',
		"19": 'nineteen',
		"20": 'twenty',
		"30": 'thirty',
		"40": 'forty',
		"50": 'fifty',
		"60": 'sixty',
		"70": 'seventy',
		"80": 'eighty',
		"90": 'ninety'
		 }

	name = name.lower()
	name = name.strip()

	formatted = []

	exclude = set(string.punctuation)

	name = ''.join(c for c in name if c not in exclude)
	
	for word in name.split():
		if word in num_dict:
			formatted.append(num_dict[word])
		elif word not in ["musical", "disneys", "the", "a"]:
			formatted.append(word)			

	return ' '.join(formatted)

# for each show, add a unique id
def add_ids(show_list, seed=1):
	show_id = seed

	for show in show_list:
		show["id"] = show_id
		show_id += 1

# Given two lists and an attribute to match on, produce a list of matches
#
# list2 are considered candidates for list1
def add_matches(list1, list2, key, verbose=False, export_file=None):
	matched = [] # list of combined dicts to be returned
	not_matched = [] # list of targets for which we could not find a match

	# For each target (item to be matched) in list1, find the best candidate 
	# match. If it is good enough, keep it.
	for target in list1:
		min_score = float("inf")
		best_match = ""

		# Get name of target show
		target_name = format_show_name(target[key].encode('ascii', 'ignore'))

		# Check for the best candidate show in list2. Keep track of the best
		# match and the optimal edit distance.
		for candidate in list2:
			candidate_name = candidate["name"].encode('ascii', 'ignore')
			candidate_name = format_show_name(candidate_name)
			dist = nltk.metrics.edit_distance(target_name, candidate_name)

			# weight distance by the length of the target name
			score = dist*1.0/len(target_name)

			if score < min_score:
				min_score = score
				best_match = candidate

		# If we found a good match, get the combined show dict and add it to
		# our combined list
		if min_score < .2:
			combine_data(target, best_match)
			matched.append(target)
			if verbose:
				print 'Matched: "{}" and "{}" {}'.format(
					target["name"], best_match["name"], min_score)
		else:
			not_matched.append(target)
			if verbose:
				print 'No Match Found: "{}" and "{}" {}'.format(
					target["name"], best_match["name"], min_score)

	if export_file:
		with open(export_file+".matched", 'w') as outfile:
			json.dump(matched, outfile)

		with open(export_file+".not.matched", 'w') as outfile:
			json.dump(not_matched, outfile)

	return matched

# Given two show dictionaries, add the information in dict2 to dict1
def combine_data(dict1, dict2):
	for key in dict2:
		if key not in dict1:
			dict1[key] = dict2[key]

	# Manually put in the entries with a duplicate key name in dict1
	if "lyrics" in dict2:
		dict1["lyrics_by"] = dict2["lyrics"]

	if "name" in dict2:
		dict1["wiki_name"] = dict2["name"]


with open('../data/shows_w_songs_w_lyrics.json.formatted', 'r') as f:
	lyrics = json.load(f)

with open('../data/wiki_data', 'r') as f:
	wiki_data = json.load(f)

# Add a unique id to each show's dictionary (different id sets for each list)
add_ids(lyrics)
add_ids(wiki_data, seed=len(lyrics)+1)

# Add a "match_id" entry to each show in lyrics list
# based on the "name" of each show
add_matches(lyrics, wiki_data, key="name", verbose=True, 
	export_file="../data/shows_combined.json")

# Join the two lists based on the "match_id" key
# joined = join_lists(lyrics, wiki_data, key="match_id")






