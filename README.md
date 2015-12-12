# Conversation Analyzer
Analyzer and statistics generator for text-based conversations.

Includes scraper and parser for Facebook conversations. 

The scraper retrieves all messages of a specific Facebook conversation and saves them in a JSON file. At this step messages include all fields and attributes as defined by the Facebook response format. [As for now the scraper doesn't work for group conversations]

The parser takes as input the result of the scraper and extracts only the textual messages and related attributes, for then saving them to a text file. Such file is used as input for the conversation analyzer.  
Conversation format example (based on the current parser):

    2012.06.17 15:27:42 SENDER_1 Message text from sender1
    2012.06.18 17:27:42 SENDER_2 Message text from sender2

##Usage
Each of the three components (i.e. scraper, parser, analyzer) can be accessed separately. 
The analyzer can be accessed via the main.py script contained in the *src* folder.
Scraper and parser are instead inside the *util* folder. 

For each see the help menu (-h or --help) for a detailed usage description.

Basic configurations for the analyzer can be managed via the *config.ini* file.  

###Scraper
In order to access Facebook conversations the following parameters are required: *cookie* and *fb_dtsg* and conversation ID. The ID of a conversation [not a group one] corresponds to the ID of the other participant.

Such data can be found via the following procedure:

1. Open the desired conversation in a browser
2. Check the network traffic via the preferred developer tool or equivalent
3. Scroll up in the conversation until a POST request is issued to [thread\_info.php](https://www.facebook.com/ajax/mercury/thread_info.php)
4. Locate and copy the required parameters (i.e. *cookie*, *fb_dtsg*, *user_ids*)

Once the values of *cookie* and *fb_dtsg* have been copied in the *config.ini* file, the scraper can be run by passing the conversation ID as argument (--id). Via the *-m* flag new messages can be merged with the previously scraped part of the same conversation, if present.

###Parser
To run the parser just provide as arguments the path of the scraped-conversation file and the desired path for the parsed output.
Additionally you can pass via *--authors* a dictionary like structure to provide a correspondence between the profile IDs and eventually preferred aliases. This might make the parsed output more readable. Example usage:

    --authors "{"11234":"SENDER_1", "112345":"SENDER_2"}"

##TODO
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

###Sequential Messages
Num of sequential messages by sender   
Delay between sequential messages by sender  

###Emoticons Stats
Total number of emoticons  
Total number of emoticons per sender  

(all previous) by hour  
(all previous) by day  
(all previous) by month  

## License

Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0