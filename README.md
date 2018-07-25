# Conversation Analyzer
Analyzer and statistics generator for text-based conversations. If interested, check out also [my related article].

Includes scraper and parser for Facebook conversations. 

The scraper retrieves all messages of a specific Facebook conversation and saves them in a JSON file. At this step messages include all fields and attributes as defined by the Facebook response format.

The parser takes as input the result of the scraper and extracts only the textual messages and related attributes, for then saving them to a text file. Such file is used as input for the conversation analyzer.  
Conversation format example (based on the current parser):

    2012.06.17 15:27:42 SENDER_1 Message text from sender1
    2012.06.18 17:27:42 SENDER_2 Message text from sender2

## **(NEW)** Download your Facebook Data
You can now download your data directly from Facebook interface. See [Access Your Information](https://www.facebook.com/your_information/) for info and instructions.
In this project we are interested solely on the *Messages* data. Once downloaded you will be able to convert the message data from JSON to the format required by this repo thanks to the convert util kindly provided by [landalex](https://github.com/landalex). See the following section for a detailed usage description.


## Usage
Run

     python setup.py install

If you downloaded your data directly from Facebook you will just need to convert it via `convert.py --in MESSAGE_ARCHIVE_JSON --out CONVERTED_FILE`.

If you instead rely on the scraping way, you can run scraper and parser via the `conversation-scraper` and `conversation-parser` commands.
See the following sections for a quick overview of the necessary steps, and check the help menu (-h or --help) for a detailed usage description.

## Scraper
Scraper has been deprecated in favor of previous more immediate method. If you still interested in using the scraper, keep in mind [this current issue](https://github.com/5agado/conversation-analyzer/issues/12).

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

## Parser
To run the parser just provide as arguments the path of the scraped-conversation file and the desired path for the parsed output.
Additionally, via *--authors*, you can pass a dictionary like structure to provide a correspondence between the profile IDs and preferred aliases. This will produce a more readable output. Example usage:

    --authors "{"11234":"SENDER_1", "112345":"SENDER_2"}"

## Analyzer
Compared to basic scraping this phase has more dependencies; see the *requirements.txt* file and [here](http://conda.pydata.org/docs/using/envs.html#share-an-environment) for a guide on how to manage environments in Conda.

**I have added two Jupyter notebooks for easier exploration of the various statistics and analytical results**. Just check out [Basic Stats](Conversation%20Analyzer%20-%20Basic%20Stats) or [Words Stats](Conversation%20Analyzer%20-%20Words%20Stats). I have left previous outputs as examples, but I encourage you to explore your own data and tweak the stats and plots based on your preferences.

If you are not familiar or not willing to check out the notebook, you can still access the old *main.py* for automatic stats running. It requires as parameter the filepath of the conversation to be analyzed; it will then log and generate a set of basic stats for the overall conversation.

### Conversation Stats List

* **Interval Stats** (start/end date, duration, days without messages)

* **Basic Length Stats** (number of messages, total length of messages, message average length)  

* **Lexical Stats** (tokens count and vocabulary, lexical diversity). Tokens count consider duplicate words, while vocabulary (also called types) is the count of unique words. Lexical richness/diversity is the ratio between vocabulary and tokens count. 

* **Word Count/Frequency** (top N words, words count, words trend, words used just by, relevant words by sender, zipf's law). This can then generalize for all other N-Grams.  

* **Emoticons Stats** (number of emoticons used, emoticon ratio, emoticon count)  

* **Reply Delay** (reply delay by sender, reply delay by message length, num of sequential messages by sender)  

* **Aggregation** - most of the previous groups include the option of aggregation by sender, or by combination of datetime features (e.g. hour, day, month, year).

**NEW**  

* **Sentiment Analysis** (joy, anger, disgust, fear values via [IBM Watson Tone Analyzer Service](http://www.ibm.com/watson/developercloud/tone-analyzer.html))

## TODO
* different-conversations comparison
* move from descriptive to predictive analytics
* option of using normal login for Facebook, then collect needed info (try mechanize)
* try analysis with [dataset_1](https://chenhaot.com/pages/changemyview.html), [??dataset_2](http://freeconnection.blogspot.fr/2016/04/conversational-datasets-for-train.html)
* better text analysis and language model of your text (from single case conversation, to join of all data you can collect) [link_1](http://textalyser.net/index.php?lang=en#analysis), [link_2]( http://www.expresso-app.org/metrics)
* combine with activity monitoring of users (e.g. Facebook)

## License

Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0
[my related article]: https://medium.com/@5agado/conversation-analyzer-baa80c566d7b#.w20u1gltf
