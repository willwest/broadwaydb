require(plyr)
require(ggplot2)
require(tm)

setwd("~/broadwaydb/analysis/")

songs <- read.csv('../data/songs.csv', stringsAsFactors=FALSE)
songs <- songs[,c("show_name", "song_name", "wiki_name", "book", "music", "lyrics_by",
                  "year", "broadway", "off_broadway", "song_count", 
                  "spotify_duration", "spotify_popularity", "spotify_track_index",
                  "spotify_track_name", "song_density","num_unique_words",
                  "vocab_diversity", "show_syllable_count",
                  "show_word_count", "album_duration", "show_density")]

head(songs)

shows <- songs[,c("show_name", "wiki_name", "book", "music", "lyrics_by",
                  "year", "broadway", "off_broadway", "song_count", "num_unique_words",
                  "vocab_diversity", "show_syllable_count",
                  "show_word_count", "album_duration", "show_density")]
shows <- unique(shows)

# count avg vocab diversity for each lyricist
lyricist_diversity <- ddply(shows, .(lyrics_by), summarize, show_count=length(show_name), avg_diversity=mean(vocab_diversity))

# distribution of song duration
ggplot(songs, aes(x=spotify_duration)) + geom_density()

# distribution of song popularity
ggplot(songs, aes(x=spotify_popularity)) + geom_density()

# distribution of vocab diversity
ggplot(shows, aes(x=vocab_diversity)) + geom_density()
