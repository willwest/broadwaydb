import pandas as pd
from pandas.tools.plotting import scatter_matrix
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn_pandas import DataFrameMapper, cross_val_score

with open('../data/songs_w_echonest.csv', 'r') as f:
    df = pd.read_csv(f)

# Get a list of the column labels in the DataFrame
df_keys = df.keys().tolist()

# Make list of only show_name, song_name, and audio columns
sel_keys = [key for key in df_keys if "audio_" in key[:6]]
sel_keys.insert(0,'song_name')
sel_keys.insert(0,'show_name')

# Cut out all columns except those in sel_keys
df_sel = df.loc[:, sel_keys]

# Drop all rows (songs) with NaN values
df_sel = df_sel.dropna()

# Group by show name
grouped = df_sel.groupby('show_name')

feature_names = [
	'audio_tempo',
	'audio_speechiness',
	'audio_valence',
	'audio_liveness',
	'audio_energy',
	'audio_danceability',
	'audio_acousticness',
	'audio_loudness'
	]

# Compose the aggregation dictionary and aggregate the grouped DataFrame
aggs = dict((feature,'mean') for feature in feature_names)
df_agg = grouped.agg(aggs)

#################
# Visualization #
#################

# Make copy of audio data
audio_data = df_agg.copy()

# Change column names for nice display
audio_keys = audio_data.columns.tolist()
audio_keys = [k.replace('audio_','') for k in audio_keys]
audio_data.columns = audio_keys


# Scatterplot Matrix of audio features
fig = scatter_matrix(audio_data, alpha=0.2, figsize=(15, 15), diagonal='kde')
plt.savefig('../figures/audio_scatter.pdf')



############
# Modeling #
############

# Compose the transformation function dict and create the mapper
mappings = [(feature, preprocessing.StandardScaler()) for feature in feature_names]
mapper = DataFrameMapper(mappings)

# Get the numpy array of the data by using the mapping
final = mapper.fit_transform(df_agg)

show_names = df_agg.index.tolist()

# Use KMeans to cluster the data
clf = KMeans(n_clusters=2)
predictions = clf.fit_predict(final)

for i,show_name in enumerate(show_names):
	print show_name, predictions[i]