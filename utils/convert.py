import json
import argparse
import heapq
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.model.message import Message
from datetime import datetime
from collections import namedtuple

# For storing messages in an object that the heap can sort
MessageTuple = namedtuple('MessageTuple', 'timestamp tiebreak_value message')

parser = argparse.ArgumentParser(description='FB Message Archive Converter')
parser.add_argument('--in', dest='archivePath', required=True, help="Path to JSON archive")
parser.add_argument('--out', dest='outPath', required=True, help="Path to output file")
args = parser.parse_args()

with open(args.archivePath, 'r') as json_file:
    data = json.load(json_file)

heap = []
message_senders = set()
tiebreaker_counter = 0
for message in data['messages']:
    message_datetime = datetime.fromtimestamp(int(message['timestamp']))
    if 'content' not in message:
        # 'content' property contains the message text, other message types (stickers, media etc) use different
        # properties which aren't handled here
        continue
    sender = message['sender_name'].encode('raw_unicode_escape').decode('utf-8')
    message_content = message['content'].encode('raw_unicode_escape').decode('utf-8')
    new_message = "{date} {time} {sender} {message}\n".format(date=message_datetime.strftime(Message.DATE_FORMAT),
                                                              time=message_datetime.strftime(Message.TIME_FORMAT),
                                                              sender=sender.replace(' ', ''),
                                                              message=message_content.replace('\n', ' '))
    heapq.heappush(heap, MessageTuple(timestamp=int(message['timestamp']), tiebreak_value=tiebreaker_counter,
                                      message=new_message))
    tiebreaker_counter += 1

sorted_messages = sorted(heap, key=lambda x: x[0])
# The messages were MessageTuples, now pull just the message string out
sorted_messages = [item.message for item in sorted_messages]
with open(args.outPath, 'w', encoding='utf-8') as out_file:
    out_file.writelines(sorted_messages)
