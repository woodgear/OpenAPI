import urllib.request as re
import re as rege
import os
import sys
import shutil




def downimage(src,path):
	def  getNameAndFromSrc(src):
		name=src[src.rindex("/")+1:len(src)-4]
		itype=src[len(src)-3:len(src)]
		return [name,itype]

	inf=getNameAndFromSrc(src)
	img=re.urlopen(src).read()
	f=open(path+'/'+inf[0]+'.'+inf[1],'wb')
	f.write(img)
	return len(img)



def downAllImageById(qid,path):
	def create(path):
		if  os.path.isdir(path):
				print('delete')
				shutil.rmtree(path)
		os.makedirs(path)

	def getpage(html):
		regexp=r'<a href="\?sort=created&amp;page=(\d*)">(\d*)</a></span>(\\n)*<span><a href="\?sort=created&amp;page=2">'
		pattern=rege.compile(regexp)
		page= pattern.findall(html)
		if len(page)==0:
			return 1
		else:
			return int(page[0][0])
		
	###############
	create(path)
	
	base="https://www.zhihu.com/question/"
	basehtml=str(re.urlopen(base+qid+'?sort=created&page=1').read())
	page=getpage(basehtml)
	
	srcs=getAllImageSrc(base+qid+'?sort=created&page=',page)
	for x in range(0,len(srcs)):
		size=downimage(srcs[x].replace('_b','_r'),path)
		print('下载图片 %d/%d  %.3f kb %s'%(x,len(srcs),size/1024,srcs[x]),end='\r')
	





def getAllImageSrc(link,page):
	srcs=[]
	iregexp=r'data-original="(https://pic\d\.zhimg\.com/[^"]*)"' #解析出图片的链接
	ipattern=rege.compile(iregexp)
	page=1
	for x in range(1,page+1):
		print(link+str(x))
		html=str(re.urlopen(link+str(x)).read())
		t=ipattern.findall(html)
		print('解析链接 %d/%d页  %d' % (x,page,len(t)),end='\r')
		srcs+=t
	return srcs


argv=sys.argv
if len(argv)==2:
	downAllImageById(argv[1],argv[1])
elif len(argv)==3:
	downAllImageById(argv[1],argv[2])
qid='41815083'
downAllImageById(qid,qid)

#TODO 如果不登录直接访问知乎的话 会有些答案看不到
#TODO 获取到的图片链接有可能是重复的
