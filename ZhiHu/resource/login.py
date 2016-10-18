import requests as req
import re as reg
import json
from requests.utils import dict_from_cookiejar
from requests.utils import cookiejar_from_dict

from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)


#从html中解析出 _xrsf
#return _xrsf
def get_xrsf(url):
	headers = {
	"Host": "www.zhihu.com",
	"Connection": "keep-alive",
	"Pragma": "no-cache",
	"Cache-Control": "no-cache",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
	"Accept": "*/*",
	"DNT": "1",
	'Referer':'https://www.zhihu.com/',
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "zh-CN,zhq=0.8,zh-TWq=0.6,enq=0.4",
	}
	r=req.get(url,headers=headers,verify=False)
	data=r.text
	regexstr=r'name="_xsrf" value="([^"]+)"'
	patt=reg.compile(regexstr)
	return patt.search(data).group(1)
	pass

#return cookie
def login(email,password):
	def logSucess(msg):
		return '登录成功'==msg['msg']

	loginUrl='https://www.zhihu.com/login/email'	
	headers = {
	"Host": "www.zhihu.com",
	"Connection": "keep-alive",
	"Pragma": "no-cache",
	"Cache-Control": "no-cache",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
	"Origin":"https://www.zhihu.com",
	"Accept": "*/*",
	'X-Requested-With':'XMLHttpRequest',
	'X-Xsrftoken':'',
	"DNT": "1",
	'Referer':'https://www.zhihu.com/',
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "zh-CN,zhq=0.8,zh-TWq=0.6,enq=0.4",
	}
	content={
	'_xrsf':'',
	'password':'',
	'captcha_type':'cn',
	'remember_me':'true',
	'email':''
	}
	cookie={
	'_xrsf':'',
	}
	global xrsf
	xrsf=get_xrsf(loginUrl)
	headers['X-Xsrftoken']=xrsf
	cookie['_xrsf']=xrsf

	content['_xrsf']=xrsf
	content['email']=email
	content['password']=password
	r=req.post(loginUrl,headers=headers,cookies=cookie,data=content,timeout=3,verify=False)
	print(json.loads(r.text))
	if logSucess(json.loads(r.text)):
		return r.cookies
	else:
		return False
	pass

def getChildTopic(pid,cid=''):
	headers = {
	"Host": "www.zhihu.com",
	"Connection": "keep-alive",
	"Pragma": "no-cache",
	"Cache-Control": "no-cache",
	"Upgrade-Insecure-Requests": "1",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
	"Accept": "text/html,application/xhtml+xml,application/xmlq=0.9,image/webp,*/*q=0.8",
	"DNT": "1",
	"Accept-Encoding": "gzip, deflate, sdch, br",
	"Accept-Language": "zh-CN,zhq=0.8,zh-TWq=0.6,enq=0.4",
	}
	moreTopic='https://www.zhihu.com/topic/19776749/organize/entire?child={0}&parent={1}'
	global cookiejar,xrsf
	url=moreTopic.format(cid,pid)
	content = {'_xsrf': xrsf}
	cookie={
	'_xsrf':'',
	'z_c0':''
	}
	cookie['_xsrf']=xrsf
	cookie['z_c0']=cookiejar.get('z_c0')
	r=req.post(url,headers=headers,cookies=cookie,data=content,timeout=3,verify=False)
	print(r.text)
	jsd=json.loads(r.text)
	return jsd


xrsf=''
cookiejar=login('yileiwei959@163.com','a4536822')
print('login ok')
if cookiejar is not False:
	print(getChildTopic('19776749'))
	pass
else:
	print('login fail')