require(plyr)
require(ggplot2)

setwd("~/broadwaydb/analysis/")

shows <- read.csv('../data/shows.csv', stringsAsFactors=FALSE)
shows <- shows[,c("show_name","wiki_name","book","music","lyrics_by",
	"with_lyrics_count","year","broadway","id","page_name","off_broadway",
	"song_count")]

head(shows)

# count number of shows by each lyricist
ddply(shows, .(lyrics_by), summarize, show_count=length(show_name))

# count number of shows by each composer
ddply(shows, .(music), summarize, show_count=length(show_name))

# count number of shows by each writer
ddply(shows, .(book), summarize, show_count=length(show_name))


######## FIGURES ##########

# distribution of song count
ggplot(shows, aes(x=song_count)) + geom_bar(binwidth=.5)

# distribtution of years
ggplot(shows, aes(x=year)) + geom_density()

