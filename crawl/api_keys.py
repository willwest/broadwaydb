import json

def get_keys():
	with open('API_KEYS.json', 'r') as f:
		keys = json.load(f)

	return keys