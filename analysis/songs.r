require(plyr)
require(ggplot2)
require(tm)

setwd("~/broadwaydb/analysis/")

songs <- read.csv('../data/songs.csv', stringsAsFactors=FALSE)
songs <- songs[,c("show_name", "song_name", "wiki_name", "book", "music", "lyrics_by",
                  "year", "broadway", "off_broadway", "song_count", "lyrics")]

head(songs)


# Fit a topic model to the lyrics
