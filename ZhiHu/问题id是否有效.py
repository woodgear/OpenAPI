from urllib.request import *
import urllib
import os
import shutil


cid=[]



for i in range(10000000,99999999):

	qid='%08d'%i
	# isOk(qid)
	try:
		html=str(urlopen('https://www.zhihu.com/question/48423072').read())
		print(html)
	except urllib.error.HTTPError :
		print (qid+' is wrong')
		continue
	print(qid+' is ok')
	cid.append(qid)


