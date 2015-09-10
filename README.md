# Conversation Analyzer
Analyzer and statistics generator for text-based conversations.

Includes scraper and parser for Facebook conversations. 

The scraper retrieves all messages of a specific Facebook conversation and saves them in a JSON file. At this step messages include all fields and attributes as defined by the Facebook response format. [As for now the scaper doesn't work for group conversations]

The parser takes as input the result of the scraper and extracts only the "relevant" messages and related attributes, for then saving them to a text file. Such file is used as input for the conversation analyzer.  
Conversation format example (based on the current parser):

    2012.06.17 15:27:42 SENDER_1 Message text from sender1
    2012.06.18 17:27:42 SENDER_2 Message text from sender2

##Usage
Each of the three components (i.e. scraper, parser, analyzer) can be accessed separately. 
The analyzer can be accessed via the main.py script contained in the top-level folder.
Scraper and parser are instead inside the util folder. 

For each see the help menu (-h or --help) for a detailed usage description.

Basic configurations for the analyzer can be managed via the config.ini file.
Here can be provided also the credentials data needed by the scraper to access the Facebook conversation.
For the scraper to work the following parameter have to be set in the config.ini file: *cookie* and *fb_dtsg*. Also the conversation ID has to be given as argument to the script. The ID of a conversation [not a group one] correpondes to the ID of the other participant.

Such data can be found via the following procedure:

1. Open the desired conversation in a browser
2. Check the network traffic via the preferred developer tool or equivalent
3. Scroll up in the conversation until a POST request is issued to [thread\_info.php](https://www.facebook.com/ajax/mercury/thread_info.php)
4. Copy the required parameters from such request

##TODO
    * emoticons via regexp
    * Generalize for group conversations (all three components)
    * NLP analyses for message, also sentiment analysis and similar
        ** consider checking emotion related to emoticon
        ** words category/sentiment (for example for word count)
    * different-conversations comparison

##Stats
###Conv Interval
Conversation start date  
Conversation end date  
Conversation duration
Days without messages

###Basic length stats
Total number of messages  
Total length of messages   
Message average length  
(all previous) by sender  

###Agglomeration Stats
(all previous) by hour  
(all previous) by day  
(all previous) by day of week  
(all previous) by month  
(all previous) by year

###Words Count (??Should be words occurrences)
Words count   
Best words count    
Word occurrences by messages agglomeration    
(all previous) by sender  
  
###Lexical Stats
Tokens count  
Distinct tokens count  
Lexical diversity  
(all previous) by sender  

###Words Mentioning
Words said by all senders  
Words said by one sender but not by the others  

###Reply Delay
Reply delay by sender (conversation with two senders)  
Reply delay by message length

##Sequential Messages
Num of sequential messages by sender   
Delay between sequential messages by sender  

##Emoticons Stats
Total number of emoticons  
Total number of emoticons per sender  

(all previous) by hour  
(all previous) by day  
(all previous) by month  

## License

Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0