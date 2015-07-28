# Conversation Analyzer
Analyzer and statistics generator for text-based conversations

##Usage

##Stats
###Conv Interval
Conversation start date  
Conversation end date  
Conversation duration  

###Basic length stats
Total number of messages  
Total number of messages per sender  
Total length of messages   
Total length of messages per sender  
Average length of messages  
Average length of messages per sender  

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

###Words Mentioning
Words said by all senders  
Words said by one sender but not by the others  

###Reply Delay
Reply delay  
Reply delay by sender (conversation with two senders)  


##TODO
    * try out a logger
    * analysis related to the time of messages 
        ** delay in reply (based on length)
        ** size based on time
    * stats based on day of the week
    * stats by month
    * stats related to emoticons (first fix problem with them. Create set)

## License

Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0