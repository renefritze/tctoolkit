'''
Matchstore.py

Stores the potential matches and finds exact matches from that list.

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/

'''

import tokenizer

class MatchData:
    '''
    store the match/duplication data of one instance
    '''
    def __init__(self,matchlen,starttoken,endtoken):
        self.matchlen = matchlen
        assert(starttoken[0] ==endtoken[0]) #make sure filenames are same
        assert(starttoken[1]<= endtoken[1]) #line number of starttoken has to be earlier than end token
        assert(starttoken[2]<= endtoken[2]) #file position of starttoken has to be earlier than end token
        self.starttoken = starttoken
        self.endtoken = endtoken
##        print "Start : ",starttoken
##        print "End : ",endtoken

    def __cmp__(self,other):
        val = cmp(self.srcfile(),other.srcfile())
        if( val==0):
            #file name is same now. Compareline numbers
            val=cmp(self.getStartLine(),other.getStartLine())
        return(val)

    def __hash__(self):
        tpl=(self.srcfile(),self.getStartLine())
        return(hash(tpl))
                    
    def getLineCount(self):
        lc = self.endtoken[1] - self.starttoken[1]
        assert(lc >=0)
        return(lc)

    def srcfile(self):
        return(self.starttoken[0])
    
    def getStartLine(self):
        return(self.starttoken[1])

class MatchSet:
    def __init__(self):
        self.matchset=set()
        self.matchedlines = None

    def addMatch(self, matchlen, matchstart, matchend):
        matchdata = MatchData(matchlen, matchstart,matchend)
        self.matchset.add(matchdata)
        lc = matchdata.getLineCount()
        if( self.matchedlines == None):
            self.matchedlines = lc
        else:
            self.matchedlines = min(self.matchedlines,lc)
        
    def __len__(self):
        return(len(self.matchset))

    def __iter__(self):
        return(self.matchset.__iter__())
    
class MatchStore:
    def __init__(self,minmatch):
        self.minmatch = minmatch
        self.hashset = dict()
        self.matchlist = dict()
        
    def addHash(self,hash, tokendata):
        hashdata = self.hashset.get(hash)
        if( hashdata == None):
            hashdata = []
        hashdata.append(tokendata)
        self.hashset[hash] = hashdata

    def getHashMatch(self,hash):
        return(self.hashset.get(hash))
    
        
    def addExactMatch(self, matchlen, sha1_hash, matchstart1,matchend1,matchstart2,matchend2):
        assert(matchstart1[0] == matchend1[0]) #ensure filenames of start and end are same
        assert(matchstart2[0] == matchend2[0]) #ensure filenames of start and end are same
        assert(matchstart1[2] < matchend1[2]) #ensure matchstart position is less than matchend position
        assert(matchstart2[2] < matchend2[2]) #ensure matchstart position is less than matchend position
        assert(matchlen >= self.minmatch)
                
        matchset = self.matchlist.get(sha1_hash)
        if(matchset == None):
            matchset = MatchSet()
        matchset.addMatch(matchlen,matchstart1,matchend1)
        matchset.addMatch(matchlen,matchstart2,matchend2)
        
        if(len(matchset)>1):
            self.matchlist[sha1_hash]= matchset
            
    def iter_matches(self):
        #print "number hashes : %d" % len(self.hashset)
        return(self.matchlist.itervalues())
            
        