from time import sleep
from time import time
import requests as req
import re as reg
import json
import pybloof as pyb
import os 
import sqlite3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)

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


"""
更新 生成知乎的话题图 DAG

"""




#话题id与名称对照表


#话题id的父子关系图
class topic(object):
	"""知乎话题的bean"""
	name=''
	id=''
	cid=''
	haschild=False
	def __init__(self,name,id,haschild,cid=''):
		super(topic, self).__init__()
		self.name=name
		self.id=id
		self.haschild=haschild
		self.cid=cid
	def __str__(self):
		return "{'name':'%s','id':'%s','haschild':'%s'}"%(self.name,self.id,self.haschild)


def log(msg):
	print(msg)
	pass






def getChildTopic(pid,cid=''):
	moreTopic='https://www.zhihu.com/topic/19776749/organize/entire?child={0}&parent={1}'
	global cppol,poolindex,headers	
	url=moreTopic.format(cid,pid)
	content = {'_xsrf': cppol[poolindex]['_xsrf']}
	r=req.post(url,headers=headers,cookies=cppol[poolindex],data=content,timeout=3,verify=False)
	jsd=json.loads(r.text)
	return jsd

	pass


def parse(jsd):
	data={'len':0,'hasmore':False,'list':[],'data':{'pid':'','cid':''}}
	items=jsd['msg'][1]
	n=len(items)
	last=items[n-1][0]
	if 'load'==last[0]:
		data['hasmore']=True
		data['data']['cid']=last[2]
		data['data']['pid']=last[3]
		n=n-1
		pass
	data['len']=n

	for i in range(0,n):
		item=items[i]
		data['list'].append(topic(item[0][1],item[0][2],False if len(item[1])==0 else True))

	return data


	pass


def totime(sec):
	sec=int(sec)
	min=sec/60
	hou=min/60
	min=min%60
	sec%=60
	return "%d:%d:%d"%(hou,min,sec)
	pass




cppol=[
#qi****@163.com
{

	'_xsrf':'48026876d8494f6be76e5996e04fc3b8',
	'z_c0':'Mi4wQUFDQWZ1a29BQUFBUUlDa3BQYXNDaGNBQUFCaEFsVk5EMTBrV0FEa2VpbDdJUDB2dGxoSGdYOW5LeldiRjhjdW9B|1476186156|568f2ce96a0c5a1f7ba57b6a6de574e98c969634'
},
#xitanzh8385@163.com
{
	'_xsrf':'4a5a437f6ffa153f87c2d094e0cabf26',
	'z_c0':'Mi4wQUFBQWdla29BQUFBa0lDU1N2ZXNDaGNBQUFCaEFsVk4wbDBrV0FDM0M0UkVPbDVZbGM4cVdVRGJyOHU5YlJybG9R|1476186333|f8e53d2860ed91d1e42b64d4232da1965c59e7bf'
}]


class sqlitedb(object):
	"""docstring for zhihuspid"""
	_path="./zhihu.db"
	_conn=""
	_sbf=""
	_cur=""
	_isfirst=True
	def __init__(self,path):
		super(sqlitedb, self).__init__()
		self._path = path
		self._conn = sqlite3.connect(self._path)
		self._cur=self._conn.cursor()
		self._isfirst=True
		def isfirst():
			ISFIRST="SELECT count(*) FROM sqlite_master WHERE type=? AND name=?"
			self._cur.execute(ISFIRST,('table','topics'))
			return int(self._cur.fetchone()[0])==0
		def create():
			CREATE_TABLE_TOPIC='CREATE TABLE topics (id text primary key,name text not null ,haschild integer default 0)'
			CREATE_TABLE_RELATION='CREATE TABLE relations (parent text not null,child text not null,unique(parent,child))'
			CREATE_TABLE_QUEUE='CREATE TABLE queue(ind integer primary key autoincrement,id text not null  unique,cid text default "",name text not null) '

			list=[CREATE_TABLE_TOPIC,CREATE_TABLE_RELATION,CREATE_TABLE_QUEUE]
			for x in list:
				self._cur.execute(x)
				self._conn.commit()

			pass
		def getblf():
			GET_BLF='SELECT id FROM topics'
			sbf=pyb.StringBloomFilter(5000000,9)
			self._cur.execute(GET_BLF)
			while True:
				t=self._cur.fetchone()
				if t is None:
					return sbf
					pass
				sbf.add(str(t[0]))
				pass

		if isfirst():
			create()
			self._sbf=pyb.StringBloomFilter(5000000,9)
			root=topic('「根话题」',"19776749",True)

			self.addTopic(root)
			self.addTopicToQueue(root)
		else:
			self._sbf=getblf() 

	def getTop(self):
		GET_TOP='SELECT name,id,cid FROM queue LIMIT 1'
		self._cur.execute(GET_TOP)
		seq=self._cur.fetchone()
		if seq is None:
			return None
			pass
		return topic(seq[0],seq[1],True)

		pass
	def deleteTop(self):
		DELETE_TOP='DELETE FROM queue WHERE id=?'
		t=self.getTop()
		if t is None:
			return False
		self._cur.execute(DELETE_TOP,(t.id,))
		self._conn.commit()
		return True
	def updateChild(self,pid,cid):
		UPDATE_QUEUE='UPDATE queue SET cid=? WHERE id=?'
		self._cur.execute(UPDATE_QUEUE,(cid,pid))
		self._conn.commit()


		pass

	def unique(self,t):
		if t.id not in self._sbf:
			self._sbf.add(t.id)
			return True
		return False
		pass
	def addTopicToQueue(self,t):
		INSERT_QUEUE='INSERT OR IGNORE INTO queue (name,id) VALUES(?,?)'
		self._cur.execute(INSERT_QUEUE,(t.name,t.id))
		self._conn.commit()

		pass
	def addTopic(self,t):
		INSERT_TOPIC='INSERT OR IGNORE INTO topics (name,id,haschild) VALUES(?,?,?)'
		self._cur.execute(INSERT_TOPIC,(t.name,t.id,1 if t.haschild else 0))
		self._conn.commit()

		pass
	def addRel(self,p,c):
		INSERT_REL='INSERT OR IGNORE INTO relations (parent,child) VALUES(?,?)'
		self._cur.execute(INSERT_REL,(p.id,c.id))
		self._conn.commit()

		pass

	def close(self):
		self._cur.close()
		self._conn.close()
		pass
	def getTopicsLen(self):
		GET_LEN='SELECT COUNT(*) FROM topics'
		self._cur.execute(GET_LEN)
		return int(self._cur.fetchone()[0])

def humanbeing():
	global count,start,db,cppol,poolindex
	count=count+1
	end=int(time())
	if count%(60*15)==0:			#每隔15分钟更换cookie (感觉没什么用 233)
		log("====> change pool %d "%((end-start)))
		poolindex=(poolindex+1)%len(cppol)
		
	if count%1==0:		#每秒发送一次请求
		sleep(1)
		log("==============(%s) %d =============="%(totime(end-start),count))
	pass

count=0
poolindex=1
cookie=cppol[poolindex]
keep=True
start=int(time())								#程序开始运行的时间


def addTo(root,list):
	sum=0
	global db
	for x in list:
		if db.unique(x):
			sum=sum+1
			db.addTopic(x)
			if x.haschild:
				db.addTopicToQueue(x)
		db.addRel(root,x)#加到话题关系中
	return sum


def retry():
	global prefailtime,fail
	if (int(time())-prefailtime)<10 and fail>3:
		return False
	prefailtime=int(time())
	fail=fail+1
	return True

def run(db):
	while True:
		t=db.get_top()#从队列中获取下一个要加载子话题的topic
		if t is None:
			print('real over')
			return True
		print("加载话题 %s"%(t.name))

		pid=t.id
		cid=t.cid
		print("%s->%s"%(t.name,cid))
		sum=0
		while True:
			jsd=''
			data=''
			try:
				jsd=getChildTopic(pid,cid)
				humanbeing()
				data=parse(jsd)				
			except json.JSONDecodeError as jse:
				print('JSON异常')
				print(jse.msg)
				print(jse.doc)
				print(jse.pos)
				if not retry():
					return False
					pass
				continue   	#json异常重试
			except  req.exceptions.RequestException as reqe:
				print(reqe)
				print("网络异常")
				if not retry():
					return False

			else:
				cou=addTo(t,data['list'])
				sum=sum+cou
				print('%s 以加载 %d  此次共%d  有效%d'%(t.name,sum,data['len'],cou))
				if data['hasmore']:
					cid=data['data']['cid']
					pid=data['data']['pid']
					db.updateChild(pid,cid)
				else:
					break

		db.delete_top()#此话题的所有一级子话题已被加载 出队


db=sqlitedb('./zhihu.db')
prefailtime=int(time())
fail=0
if run(db):
	print("下载完成 获得了 %d 个话题"%(db.getTopicsLen()))
else:
	print('失败')
db.close()
print(totime(int(time())-start))

#知乎话题有一个页面下面会有子话题共有xx子话题的 可以利用这个来进行更新判断