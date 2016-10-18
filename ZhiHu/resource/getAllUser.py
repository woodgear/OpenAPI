from time import sleep
from time import time
import requests as req
import re as reg
import json
import pybloof as pyb
import sqlite3
from misaki_tools import read_file_as_string, send_mail, log

from requests.packages.urllib3.exceptions import InsecureRequestWarning

req.packages.urllib3.disable_warnings(InsecureRequestWarning)


# 首先将cookie放到外面 有一个重新读取的功能
# 直接在数据库初始化吧
# 前提是用getTopic得到了话题的数据库
# create table topic_desc (id text primary key,cout integer default 0,desc text default '', foreign key(id) references topics(id))
# create table users (id integer primary key autoincrement,sid text not null unique,name text ,desc text default '')
# create table queue (id text primary key,name text,offset integer default 0)
# insert into queue  select id,name,0 from topics
# 仔细想了想 还是不加入 话题和用户之间的关系了 毕竟 加了好像也没什么用 而且如果一定要加的话 获取用户id 什么的也很麻烦
class QueueIem(object):
    """根据话题抓取用户 这是话题队列的item"""

    def __init__(self, dic):
        super(QueueIem, self).__init__()
        self.dict = dic
        self.id = dic['id']
        self.name = dic['name']
        self.offset = dic['offset']

    def __str__(self):
        return str(self.dict)


class User(object):
    """docstring for user"""

    def __init__(self, dic):
        super(User, self).__init__()
        self.id = dic['id']
        self.name = dic['name']
        self.desc = dic['desc']
        self.dic = dic

    def __str__(self):
        return str(self.dic)
        pass


class SqliteDB(object):
    def __init__(self, path):
        super(SqliteDB, self).__init__()
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()

        def get_blf():
            GET_BLF = 'SELECT sid FROM users'
            sbf = pyb.StringBloomFilter(100000000, 9)
            self.cur.execute(GET_BLF)
            counter = 0
            while True:
                t = self.cur.fetchone()
                counter += 1
                if t is None:
                    log('加载 %d 项' % counter)
                    return sbf
                    pass
                sbf.add(str(t[0]))
                pass

        self.sbf = get_blf()
        log('布隆过滤器初始化完毕')

    def get_top(self):
        GET_TOP = 'SELECT name,id,offset FROM queue LIMIT 1'
        self.cur.execute(GET_TOP)
        seq = self.cur.fetchone()
        if seq is None:
            return None
            pass
        return QueueIem({'name': seq[0], 'id': seq[1], 'offset': seq[2]})
        pass

    def delete_top(self):
        DELETE_TOP = 'DELETE FROM queue WHERE id=?'
        t = self.get_top()
        if t is None:
            return False
        self.cur.execute(DELETE_TOP, (t.id,))
        self.conn.commit()
        pass

    def update(self, id, offset):
        UPDATE = 'UPDATE queue SET offset=? WHERE id=?'
        self.cur.execute(UPDATE, (offset, id))
        self.conn.commit()
        pass

    def add_topic_desc(self, id, followers, desc):
        """
        :param id:
        :param followers:
        :param desc:
        :return:
        """
        ADD_TOPIC_DESC = 'INSERT OR REPLACE INTO topic_desc (id,count,desc) values(?,?,?)'
        self.cur.execute(ADD_TOPIC_DESC, (id, followers, desc))
        self.conn.commit()
        pass

    def add_user_list(self, lis):
        ADD_USER = 'INSERT OR REPLACE INTO users (sid,name,desc) values(?,?,?)'
        counter = 0
        for x in lis:
            if self.unique(x.id):
                counter += 1
                self.cur.execute(ADD_USER, (x.id, x.name, x.desc))
                self.conn.commit()
        return counter
        pass

    def unique(self, id):
        if id not in self.sbf:
            self.sbf.add(id)
            return True
        return False
        pass

    def close(self):
        self.cur.close()
        self.conn.close()
        pass


# 去除所有 TAG
def clear(data):
    lis = []
    FLAG = 0
    for x in data:
        if x == '<' or x == '>':
            FLAG = (FLAG + 1) % 2
        if x != '>' and FLAG == 0:
            lis.append(x)
    return ''.join(lis)


# 是不是应该把他放到函数体中呢？
countreg = r'<a href="/topic/\d+/followers"><strong>(\d+)</strong></a> 人关注了该话题'
conutpattern = reg.compile(countreg)
descreg = r'<div id="zh-topic-desc"[^>]*>\n<div class="zm-editable-content" [^>]*>(.*)</div>\n</div>'
descpattern = reg.compile(descreg)


def parse_desc(r):
    """
    接解析话题的html 获得话题描述 话题的关注人数
    """
    # 有可能出现 正常 过于频繁 话题被删除3种可能
    global desc_count_reg_pattern, desc_desc_reg_pattern, tofast_reg_pattern
    data = r.text
    status = r.status_code
    count_match = desc_count_reg_pattern.findall(data)
    desc_match = desc_desc_reg_pattern.findall(data)

    if status == 200 and len(count_match) != 0 and len(desc_match) != 0:  # 正常捕获
        return {'status': 0, 'count': count_match[0], 'desc': desc_match[0]}
    elif status == 200 and is_tofast(data):  # 过于频繁
        return {'status': 1}
    return {'status': 2}


class CookieManager(object):
    """管理cookie的类"""

    def __init__(self, path):
        self.path = path
        self.update()
        self.index = 0

    def get(self):
        if len(self.pool) == 0:
            self.update()
        return self.pool[self.index]

    def change(self):
        self.index = (self.index + 1) % len(self.pool)

    def update(self):
        def init_cookie_pool(data):
            lis = []
            for x in data:
                if x['useful'] != 0:
                    lis.append({'z_c0': x['z_c0'], '_xsrf': x['_xsrf']})
            return lis

        while True:
            cookie_data = json.loads(read_file_as_string(self.path))
            # noinspection PyAttributeOutsideInit
            self.pool = init_cookie_pool(cookie_data)
            if not self.empty(): break
            log("请更新cookie")
            send_mail('请更新cookie')
            sleep(60)

    def wrongcookie(self):
        del self.pool[self.index]
        if self.empty():
            self.update()
        pass

    def empty(self):
        return len(self.pool) == 0


# noinspection PyShadowingNames
def spider_desc(id, cookie):
    """
    根据话题id 获取此话题的 html
    :param cookie:
    :param id: 话题id
    :return:
    """
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
    url = 'https://www.zhihu.com/topic/{0}/manage'  # 从管理这里获取信息
    url = url.format(id)
    return req.get(url, headers=headers, cookies=cookie, verify=False)


# 获取此话题的关注的
def spider_user_list(id, cookie, offset=0):
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
        'X-Requested-With': 'XMLHttpRequest',
        'X-Xsrftoken': ''
    }
    url = 'https://www.zhihu.com/topic/{0}/followers'
    url = url.format(id)
    headers['X-Xsrftoken'] = cookie['_xsrf']
    con = {'offset': offset}
    return req.post(url, headers=headers, cookies=cookie, data=con, verify=False)


def parse_user_list(r):
    data = r.text
    if is_tofast(data):
        return {"status": 1}
    data = json.loads(data)['msg']
    global userlist_reg_pattern
    lis = []
    if data[0] != 0:
        for x in userlist_reg_pattern.findall(data[1]):
            lis.append(User({'id': x[0], 'name': x[1], 'desc': x[3]}))
    return {'status': 0, 'data': lis}


# noinspection PyShadowingNames
def get_all_user(db, cm):
    while True:
        try:
            t = db.get_top()  # 获取话题
            log("加载话题 %s %s " % (t.name, t.id))
            if t is None:  # 已经没有话题了结束
                return True
            info = parse_desc(spider_desc(t.id, cm.get()))  # 获取此话题的关注的人数和话题的描述
            humanbeing()
            status = info['status']
            if status == 0:  # 正常
                db.add_topic_desc(t.id, info['count'], info['desc'])
            elif status == 1:  # 频繁
                cm.wrongcookie()
                continue
            elif status == 2:  # 其他
                db.delete_top()
                log('获取描述 其他情况 ' + str(info))
                continue
            log("%s 描述=> %s" % (t.name, info['desc']))

            db.add_topic_desc(t.id, info['count'], info['desc'])  # 插入描述到数据库中

            offset = t.offset
            counter = 0
            while True:
                humanbeing()
                res = parse_user_list(spider_user_list(t.id, cm.get(), offset))
                lis = []
                if res['status'] == 0:
                    lis = res['data']
                else:
                    cm.wrongcookie()
                    continue

                log('此次获取 %d 个用户' % len(lis))
                if len(lis) == 0:  # 以获取的json数据为判断标准
                    log("此话题共获取用户 %d 个" % counter)
                    break
                use = db.add_user_list(lis)  # 将用户加入数据库中
                log("有效 %d个 offset %d sum %d" % (use, offset, counter))
                counter = counter + use
                offset += len(lis)  # 更新偏移  #这里有问题 因为很可能会有新的用户关注 这样就重复了 不过如果够快的话应该没问题
                db.update(t.id, offset)  # 更新数据库中话题队列的偏移值
            db.delete_top()  # 这样一个话题的关注用户就完成了
            # 可能有的异常是 网络中断 json解析错误
        except json.JSONDecodeError as jse:
            print(jse.msg)
            print(jse.doc)
            print(jse.lineno)


def is_tofast(data):
    global tofast_reg_pattern
    return tofast_reg_pattern.search(data) is not None
    pass


def totime(sec):
    sec = int(sec)
    min = sec / 60
    hou = min / 60
    min %= 60
    sec %= 60
    return "%d:%d:%d" % (hou, min, sec)


count = 0


def humanbeing():
    global count, start, cm
    count += 1
    end = int(time())
    if count % 1000 == 0:  # 更换cookie (感觉没什么用 233)
        log("====> change pool %d " % (end - start))
        cm.change()

    if count % 10 == 0:
        sleep(1)
        log("==============(%s) %d ==============" % (totime(end - start), count))
    pass


desc_count_reg_pattern = reg.compile(r'<a href="/topic/\d+/followers"><strong>(\d+)</strong></a> 人关注了该话题')
desc_desc_reg_pattern = reg.compile(
    r'<div id="zh-topic-desc"[^>]*>\n<div class="zm-editable-content" [^>]*>(.*)</div>\n</div>')
userlist_reg_pattern = reg.compile(
    r'<a href="/people/([^"]*)" class="zg-link author-link">([^<]*)</a>\s*</h2>\s*<div class="summary-wrapper summary-wrapper--medium">\s(<span title="[^"]*" class="bio">\s([^<]*)\n</span>)?')
tofast_reg_pattern = reg.compile(
    r'<div class="page_form_wrap c r5px">\n<p>非常抱歉，您的帐号由于访问频次过快，已被暂时限制使用。您可以使用注册邮箱联系 <a href="mailto:i@zhihu.com">i@zhihu.com</a> 反馈情况。</p>\n</div>')

start = int(time())
db = SqliteDB('./zhihuUser.db')
cm = CookieManager("./cookiepool.json")
get_all_user(db, cm)
db.close()
log(int(time()) - start)
send_mail("over")
