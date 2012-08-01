'''
Code Duplication Detector
using the Rabin Karp algorithm to detect duplicates

Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at http://code.google.com/p/tctoolkit/
'''

import matchstore
from rabinkarp import RabinKarp
from tokenizer import Tokenizer
import tempfile
import os
import shutil

class CodeDupDetect:
	def __init__(self,filelist, minmatch=100):
		self.matchstore = matchstore.MatchStore(minmatch)
		self.minmatch = minmatch #minimum number of tokens to be matched.
		self.filelist = filelist
		self.foundcopies = False

	def __findcopies(self):
		totalfiles = len(self.filelist)
		i=0
		for srcfile in self.filelist:
				i=i+1
				print "Analyzing file %s (%d of %d)" %(srcfile,i,totalfiles)
				tknzr = Tokenizer(srcfile)
				rk = RabinKarp(self.minmatch,self.matchstore)
				rk.addAllTokens(tknzr)
		self.foundcopies = True

	def findcopies(self):
		if( self.foundcopies == False):
				self.__findcopies()
		return(self.matchstore.iter_matches())

	def printmatches(self,output):
		exactmatches = self.findcopies()
		#now sort the matches based on the matched line count (in reverse)
		exactmatches = sorted(exactmatches,reverse=True,key=lambda x:x.matchedlines)
		matchcount=0

		for matches in exactmatches:
				output.write('%s\n'%('='*50))
				matchcount=matchcount+1
				output.write("Match %d:\n"%matchcount)
				fcount = len(matches)
				first = True
				for match in matches:
						if( first):
								output.write("Found an approx. %d line duplication in %d files.\n" % (match.getLineCount(),fcount))
								first = False
						output.write("Starting at line %d of %s\n" % (match.getStartLine(),match.srcfile()))

		return(exactmatches)

	def insert_comments(self):
		begin_no = 0
		for matches in sorted(self.findcopies(),reverse=True,key=lambda x:x.matchedlines):
			for match in matches:
				fn = match.srcfile()
				infostring = ' '.join(['%s:%i+%i'%(f.srcfile(),f.getStartLine(),f.getLineCount()) for f in matches if f.srcfile() != fn])
				tmp_source = tempfile.NamedTemporaryFile(mode='wb', delete=False, prefix='cdd-')
				with open(fn, 'r') as srcfile:
					for i in range(match.getStartLine()):
						tmp_source.write(srcfile.readline())
					comment = '//!DUPLICATE BEGIN %i -- %s\n'%(begin_no, infostring)
					tmp_source.write(comment)
					for i in range(match.getLineCount()):
						line = srcfile.readline()
						tmp_source.write(line)
						with open('/tmp/%i.dup'%begin_no, 'a') as dup:
							dup.write(line)
					comment = '//!DUPLICATE END %i\n'%begin_no
					tmp_source.write(comment)
					line = srcfile.readline()
					while line:
						tmp_source.write(line)
						line = srcfile.readline()
				#this should also work on windows
				tmp_source_name = tmp_source.name
				tmp_source.close()
				shutil.copy(tmp_source_name, fn)
				begin_no += 1