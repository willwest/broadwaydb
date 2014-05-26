## Broadway (and Off-Broadway) Musical Analysis

### Table of Contents
* [Source](#source)
* [Developers](#developers)
* [Background](#background)
* [Data Collection](#data-collection)

<hr>

### Source
This project currently consists of three modules:
* `crawl`: code for scraping lyrics and accessing APIs
* `munge`: scripts for formatting and joining data
* `analysis`: R code for data exploration

### Developers
* "Will West" wmw71190@gmail.com

### Data Collection
For this project, several types of data are needed. First, lyrics are needed
to capture the topics and lexical characteristics of each song and show.
Metadata about each show and song is also necessary, so we can model the
patterns that emerge between different composers and artists.

### Background
The goal of this project is to better understand the measurable
characteristics of musicals, and the patterns that emerge among different
types of shows.

While there has been a lot of work done in analyzing music in
general, often musicals are lumped into the soundtrack category without 
specific attention given to their unique characteristics. This results in 
recommendation systems and music discovery applications that don't properly
capture a user's tastes when it comes to musicals.

#### What makes musicals unique?

##### Subject matter
Musicals tend to delve heavily into one or more topics that may set it apart
from other musicals. While lyrics in traditional genres may address specific
emotions (love, anger, etc.) or cultures (pop culture, politics, etc.),
a musical can revolve completely around a single topic. Take for example
the popular broadway musical Next to Normal. The entire musical is focused
on mental health, treatments, and the way both can positively and negatively
impact a family.

##### Composer, Lyricist, Artist Loyalties/Preferences
While traditionally albums are composed and performed by a single artist, 
musicals often are composed by a single composer and performed by several
different artists. A listener's opinion of a musical album may be impacted
by both an affinity towards the composer/lyricist, and a mixture of
preferences for each artist featured on the album.
