import urllib.request as re
import re as rege
import os
import shutil
def  getNameAndFromSrc(src):
	name=src[src.rindex("/")+1:len(src)-4]
	itype=src[len(src)-3:len(src)]
	return [name,itype]

def create(path):
	if  os.path.isdir(path):
			shutil.rmtree(path)
	os.makedirs(path)
	pass

def downimage(src,path):
	inf=getNameAndFromSrc(src)
	img=re.urlopen(src).read()
	f=open(path+'/'+inf[0]+'.'+inf[1],'wb')
	f.write(img)
	return len(img)



def downAllImageById(qid,path):
	create(path)
	base="https://www.zhihu.com/question/"
	basehtml=str(re.urlopen(base+qid+'?sort=created&page=1').read())
	page=getpage(basehtml)
	srcs=getAllImageSrc(base+qid+'?sort=created&page=',page)
	for x in range(0,len(srcs)):

		size=downimage(srcs[x].replace('_b','_r'),path)
		print('下载图片 %d/%d  %.3f kb'%(x,len(srcs),size/1024),end='\r')
		pass
	


def getpage(html):
	regexp=r'<a href="\?sort=created&amp;page=(\d*)">(\d*)</a></span>(\\n)*<span><a href="\?sort=created&amp;page=2">'
	pattern=rege.compile(regexp)
	page= pattern.findall(html)[0][0]
	return (int(page))

def parseimagesrc(html):

	pass

def getAllImageSrc(link,page):
	srcs=[]
	iregexp=r'<img src="(https://pic\d\.zhimg\.com/[^"]*_b[^"]*)"'
	ipattern=rege.compile(iregexp)
	
	for x in range(1,page+1):
		html=str(re.urlopen(link+str(x)).read())
		t=ipattern.findall(html)
		print('解析链接 %d/%d页  %d' % (x,page,len(t)),end='\r')
		srcs+=t
	return srcs

qid='46312145'
argv=os.argv
if len(argv)==1:
	downAllImageById(argv[0],argv[0])
elif len(argv)==2:
	downAllImageById(argv[0],argv[1])


