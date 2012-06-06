#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import sys,os

def start():
	print "="*50,"\n\f wc - print newline, word, and byte counts for each file\f\n","="*50
	#

def main(File,file_name):	
	try:
		lines = File.readlines()
	except IOError:
		print "WARRING!"
	finally:
		File.close()

	b = 0
	for x in xrange(len(lines)):
		b +=len(lines[x])

	l = len(lines)
	print l,'lines',b,'byte','--%s'%file_name[-1]

def open_file(path):
	try:
		File = open(path,'r')
	except IOError:
		print "File not found!"
		sys.exit()
	except:
		print "I don't know ?"
	else:
		return File

def FileName(path):
	file_name = path.split('/')
	return file_name



start()
path = raw_input(">:")
#################################
if path == 'ls':
	ls = os.listdir(os.getcwd())
	print ls
	sys.exit()
#################################
File = open_file(path)
name = FileName(path)
main(File,name)