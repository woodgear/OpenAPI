import urllib.request as re
import urllib.parse as pr
import re as rege


def getImageSrc(html):
	base="https://www.bing.com"
	imgsrcpattern=rege.compile(r'g_img={url: "([^"]*)"')
	imagesrc= imgsrcpattern.findall(html)[0]
	return base+imagesrc

def getImageTitle(html):
	titlepattern=rege.compile(r'<a id="sh_cp" class="sc_light"\s*title="([^"]*)"')
	title=titlepattern.findall(html)[0].replace('\\x','%')
	title=pr.unquote(title)
	return title




html=str(re.urlopen("https://www.bing.com/").read())
imagesrc=getImageSrc(html)
title=getImageTitle(html)
print(imagesrc+" "+title)
print("over")