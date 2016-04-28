import urllib.request as re
import re as rege


def getBingImgsrc():
  bing=re.urlopen("https://www.bing.com/")
  html=str(bing.read())
  base="https://www.bing.com"
  pattern=rege.compile(r'g_img=\{url:\\\'([^,]*\.jpg)')
  imagesrc= pattern.findall(html)[0]
  return base+imagesrc



print(getBingImgsrc())


