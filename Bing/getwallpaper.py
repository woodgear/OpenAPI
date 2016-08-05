import urllib.request as re
import urllib.parse as pr
import re as rege
"""
www.bing.com/az/hprichbg/rb/WildGardens_ZH-CN12707941302_1920x1080.jpg
							名字						 尺寸	   类型

"""
#从html代码中获得壁纸链接
def getImageSrc(html):
	base="https://www.bing.com"
	imgsrcpattern=rege.compile(r'g_img={url: "([^"]*)"')
	imagesrc= imgsrcpattern.findall(html)[0]
	return base+imagesrc

#从html代码中获取壁纸描述 地点 作者
def getDescribe(html):
	allpattern=rege.compile(r'<a id="sh_cp" class="sc_light"\s*title="([^"]*)"')
	alldes=allpattern.findall(html)[0].replace('\\x','%')
	alldes=pr.unquote(alldes)
	describepattern=rege.compile(r"([^，]*)，([^(]*)\(© ([^/]*)")
	describe=describepattern.findall(alldes)[0]

	return describe
#从壁纸链接中获得壁纸尺寸
def getsize(src):
	sizepattern=rege.compile(r"_(\d*)x(\d*)")
	size=sizepattern.findall(src)[0]
	return size
	pass

#从壁纸链接中获得壁纸名字
def getTitle(src):
	titlepattern=rege.compile(r"rb/([^_]*)")
	title=titlepattern.findall(src)[0]
	return title
	pass
#从壁纸链接中获得图片类型
def getType(src):
	return src[-3::]

	pass
html=str(re.urlopen("https://www.bing.com/").read())#获取bing首页html
imagesrc=getImageSrc(html)#获取壁纸链接
describe=getDescribe(html)#获取描述
size=getsize(imagesrc)
title=getTitle(imagesrc)
imgtype=getType(imagesrc)




bwjsonmode='{{"src":"{0}","title":"{1}","width":{2},"height":{3},"describe":"{4}","location":"{5}","author":"{6}" }}'
bwjson=bwjsonmode.format(imagesrc,title,size[0],size[1],describe[0],describe[1],describe[2])
