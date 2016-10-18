import requests as req
import re as reg
import pybloof as pyb

# link='http://www.misakimei.com'
# link='http://pic1.zhimg.com/16093960c_m.jpg'
headers = {
    "Host": "www.zhihu.com",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "DNT": "1",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.6,en;q=0.4",
    "Cookie": 'z_c0=Mi4wQUFDQWJPNG9BQUFBUU1EUHFtT2xDaGNBQUFCaEFsVk5hS2djV0FEZUVIdVZFeE82bWVqSkZoUGhtLXU1N2sxNG9R|1475685950|0498ba35e2fc82a0ca1c46fcb6d26292a273a7bf'
}

link = 'https://www.zhihu.com/people/{0}/followees'

users = ["rosicky311"]
regexp = r'https://www.zhihu.com/people/([^"/]*)"'
pattern = reg.compile(regexp)
path = "/zhihuuser/"


def save(name, text):
    f = open(path + name + ".html", 'w', encoding="utf-8")
    f.write(text)
    f.close()
    print("%s 保存完成" % (name))
    pass


def get(user):
    url = link.format(user)
    r = req.get(url, headers=headers, verify=False)
    data = r.text  # 获取到此用户关注列表
    save(user, data)  # 保存到磁盘中

    match = pattern.findall(data)  # 解析出关注列表
    for x in match:
        if not x in sbf:
            users.append(x)  # 增加用户
            sbf.add(x)
            print("增加新用户 %s   =>%d" % (x, len(users)))
        pass
    pass


def saveuser(num):
    f = open(path + 'user.txt', 'a', encoding="utf-8")
    for x in range(num, num + savestep + 1):
        f.writelines(users[x] + "\n")
    f.close()


sbf = pyb.StringBloomFilter(100000000, 9)

index = 0
savestep = 100
presave = 0
while index < len(users):
    get(users[index])
    index = index + 1

    if len(users) - presave > savestep:
        saveuser(presave)
        presave = presave + savestep
        print("保存 %d" % (presave))


        # if len(users)>100:
        # 	break
