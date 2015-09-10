# -*- coding: utf-8 -*-

import re
import util.io as mio

test = re.compile("""(
#Western
[<>\}30o]?
[:;=8bx]                     # eyes
[\-o\*\']?                 # optional nose
[\)\]\(\[dpi3/\:\}\{@\|\\\]* #mouth
|
[\)\]\(\[dp3/\:\}\{@\|\\\] #mouth
[\-o\*\']?                 # optional nose
[:;=8bx]                     # eyes
[<>]?
|
#Eastern
[><\-ùu\+\*èçòû\^] #eye
[\-_\.]* #nose
[><\-ùu\+\*èçòû\^]#eye
[\']?
|
<3
)""", re.IGNORECASE|re.VERBOSE)

#pattern = """[[<>\}30o]?[:;=8bx][\-o\*\']?[\)\]\(\[dp3/\:\}\{@\|\\]]"""
#pattern = "[:;][dp]"

def printMatchesIn(text):
    emoticons = mio.getSetFromFile(mio.getResourcesPath() + "\emoticonList.txt")
    for e in emoticons:
        matches = [(e[a.start(): a.end()]) for a in list(test.finditer(e))]
        if len(matches) == 0 or matches[0] != e:
            print(e)

printMatchesIn("Hello xDDD xH How are you ;d *__*")