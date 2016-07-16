import urllib.request as re
import re as rege
import os
import shutil
def  getNameAndFromSrc(src):
	name=src[src.rindex("/")+1:len(src)-4]
	itype=src[len(src)-3:len(src)]
	return [name,itype]

def create(path):
	if not os.path.isdir(path):
		os.makedirs(path)
	pass

def downimage(src,path):
	create(path)
	inf=getNameAndFromSrc(src)
	img=re.urlopen(src)
	f=open(path+'/'+inf[0]+'.'+inf[1],'wb')
	f.write(img.read())


def downAllImageById(qid,path):
	base="https://www.zhihu.com/question/"
	regexp=r'<img src="(https://pic\d\.zhimg\.com/[^"]*_b[^"]*)"'
	html=str(re.urlopen(base+qid).read())
	pattern=rege.compile(regexp)
	imagesrc= pattern.findall(html)
	print('共'+str(len(imagesrc)))
	for x in range(0,len(imagesrc)):
		downimage(imagesrc[x],path)
		print(str(x)+' ok')
	pass



qid='48456893'
downAllImageById(qid,qid)


