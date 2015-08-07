# Conversation Analyzer
Analyzer and statistics generator for text-based conversations.

Current conversation format example:

    2012.06.17 15:27:42 SENDER_1 Message text from sender1
    2012.06.18 17:27:42 SENDER_2 Message text from sender2

##Usage
In order to use it just run the main.py script contained in the top-level folder.
See the help menu (-h or --help) for a detailed usage description.

Basic configurations can be managed via the config.ini file.

##Stats
###Conv Interval
Conversation start date  
Conversation end date  
Conversation duration
Days without messages

###Basic length stats
Total number of messages  
Total number of messages per sender  
Total length of messages   
Total length of messages per sender  
Message average length  
Message average length per sender  

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

###Words Count
Words count  
Words count by sender  
Best words count  
Best words count by sender  
Word occurences by message agglomeration
Word occurences by message agglomeration by sender

###Words Mentioning
Words said by all senders  
Words said by one sender but not by the others  

###Reply Delay
Reply delay (does overall delay make sense?)  
Reply delay by sender (conversation with two senders)  
Reply delay by messsage length

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