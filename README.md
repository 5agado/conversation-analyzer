# Conversation Analyzer
Analyzer and statistics generator for text-based conversations.

Includes scraper and parser for Facebook conversations. 

The scraper retrieves all messages of a specific Facebook conversation and saves them in a JSON file. At this step messages include all fields and attributes as defined by the Facebook response format.

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

(all previous) mean  
(all previous) median  
(all previous) mode  
(all previous) mean deviation  
(all previous) variance  
(all previous) standard deviation  

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
Reply delay (does overall delay make sense?)  
Reply delay by sender (conversation with two senders)  
Reply delay by message length

##Sequential Messages
Num of sequential messages by sender   
Delay between sequential messages by sender  

##Emoticons Stats
Total number of emoticons  
Total number of emoticons per sender  

(all previous) by day  
(all previous) by month  

##TODO
    * NLP analyses for message, also sentiment analysis and similar
        ** consider checking emotion related to emoticon
        ** words category/sentiment (for example for word count)
    * clean and include facebook scraper

## License

Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0