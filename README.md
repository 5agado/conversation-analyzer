# Conversation Analyzer
Analyzer and statistics generator for text-based conversations. If interested, check out also [my related article].

Includes scraper and parser for Facebook conversations. 

The scraper retrieves all messages of a specific Facebook conversation and saves them in a JSON file. At this step messages include all fields and attributes as defined by the Facebook response format.

The parser takes as input the result of the scraper and extracts only the textual messages and related attributes, for then saving them to a text file. Such file is used as input for the conversation analyzer.  
Conversation format example (based on the current parser):

    2012.06.17 15:27:42 SENDER_1 Message text from sender1
    2012.06.18 17:27:42 SENDER_2 Message text from sender2

##Usage
Each of the three components (i.e. scraper, parser, analyzer) can be run separately. 
The analyzer can be accessed via the *main.py* script contained in the *src* folder. It will log a set of basic stats for the overall conversation.
Scraper ( *conversationScraper.py* ) and parser ( *conversationParser.py* ) are instead inside the *util* folder. 

For each see the help menu (-h or --help) for a detailed usage description.

Basic configurations for all modules can be managed via the *config.ini* file. The location of the config file to be used should be passed via *--config* argument.   

###Requirements
The only additional requirement for parser and scraper is the *requests* package. For the analyzer I used Conda; *requirements.txt* is the exported environment file. See [here](http://conda.pydata.org/docs/using/envs.html#share-an-environment) for a guide on how to manage Conda environments.

##Scraper
In order to access Facebook conversations the following parameters are required: *cookie* and *fb_dtsg* and conversation ID.

Such data can be found via the following procedure:

1. Open the desired conversation in a browser
2. Check the network traffic via the preferred developer tool or equivalent
3. Scroll up in the conversation until a POST request is issued to [thread\_info.php](https://www.facebook.com/ajax/mercury/thread_info.php)
4. Locate and copy the required parameters: *cookie*, *fb_dtsg* and conversation ID  
4.1 You can find the conversation ID in a line with this format: *messages\[user_ids\]\[\<conversation_ID\>\]..* or *messages\[thread_fbids\]\[\<conversation_ID\>\]* for group conversations.

Once the values of *cookie* and *fb_dtsg* have been copied in the *config.ini* file, the scraper can be run by passing the conversation ID as argument (--id). 
If you want to scrape a group conversation, use the *-g* flag, the scraper will not work otherwise.
Via the *-m* flag new messages can be merged with the previously scraped part of the same conversation, if present.

##Parser
To run the parser just provide as arguments the path of the scraped-conversation file and the desired path for the parsed output.
Additionally, via *--authors*, you can pass a dictionary like structure to provide a correspondence between the profile IDs and preferred aliases. This will produce a more readable output. Example usage:

    --authors "{"11234":"SENDER_1", "112345":"SENDER_2"}"

##Analyzer
**The analyzer is still a work in progress.**

I have added a **ipython notebook for easier exploration of the various statistics and analytical results**. Just check out the *conversation-analyzer.ipynb* in the top-level folder. I have left previous outputs as examples, but I encourage you to explore your own data and tweak the stats and plots based on your preferences. If you are not familiar or not willing to check out the notebook, you can still access the old *main.py* for automatic stats running. It requires as parameter the filepath of the conversation to be analyzed; it will then log and generate a set of basic stats for the overall conversation.

Related classes are in the *stats* folder. The suggested and maintained class to use is *convStatsDataframe*, that makes use of Pandas *Dataframe* for the stats generation. In the *test* package you can find unittests and example files that generate or plot different kind of statistics.

* **Conv Interval** (start date, end date, duration, days without messages)

* **Basic length stats** (number of messages, total length of messages, message average length)  

* **Lexical Stats** (tokens count and vocabulary, lexical diversity)  

* **Word Count/Frequency** (top N words, word count, words said just by, tf-idf, relevant words by sender, zipf's law)  

* **N-Gram Count/Frequency** (bi and trigrams by sender, tf-idf)

* **Emoticons Stats** (number of emoticons, emoticon ratio, emoticon count)  

* **Reply Delay** (reply delay by sender, reply delay by message length, num of sequential messages by sender)  

* **Aggregation**: most of the previous groups include the option of aggregation by sender, or by datetime features (e.g. hour, day, month, year) where relevant

**NEW**  

* **Sentiment Analysis** (joy, anger, disgust, fear values via [IBM Watson Tone Analyzer Service](http://www.ibm.com/watson/developercloud/tone-analyzer.html))

##TODO
    * different-conversations comparison
    * option of using normal login for facebook, then collect needed info (try mechanize)

## License

Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0
[my related article]: https://medium.com/@5agado/conversation-analyzer-baa80c566d7b#.w20u1gltf