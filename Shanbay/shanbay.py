import requests
import json


def cacl_page_size(total, ipp):
    return round(float(total)/ipp+0.5)


class Shanbay:
    master_word_url = "https://www.shanbay.com/api/v1/bdc/library/master/"
    resolved_word_url = "https://www.shanbay.com/api/v1/bdc/library/resolved/"

    cookies = ''
    headers = {
        'DNT': "1",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        'Accept': "*/*",
        'Referer': "https://www.shanbay.com/bdc/learnings/library/",
        'X-Requested-With': "XMLHttpRequest",
        'Connection': "keep-alive",
        'Cache-Control': "no-cache",
    }

    def __init__(self, config):
        self.config = config
        self.cookies = "userid={};auth_token={};sessionid={}".format(
            config['userid'], config['auth_token'], config['sessionid'])
        self.headers['Cookie'] = self.cookies
        pass
    # {"page": page, "_": "1529847629180"}
    # ret "{"total":2,"page":1,"ipp":10,"words":["apple","tree"]}"

    def get_word(self, url, page):
        res = requests.request("GET", url, headers=self.headers, params={
                               "page": page, "_": "1529847629180"})
        res = json.loads(res.text)
        ret = {}
        ret['total'] = res['data']['total']
        ret['page'] = res['data']['page']
        ret['ipp'] = res['data']['ipp']
        ret['words'] = list(
            map(lambda word: word['content'], res['data']['objects']))
        return ret

    def get_all_know_word(self):
        return list(set(self.get_all_master_word()+self.get_all_resolved_word()))

    def get_all_resolved_word(self):
        return self.get_word_by_url(self.resolved_word_url)

    def get_all_master_word(self):
        return self.get_word_by_url(self.master_word_url)

    def get_word_by_url(self, url):
        words = []
        res = self.get_word(url, 1)
        words += res['words']
        page_size = cacl_page_size(res['total'], res['ipp'])
        for page in range(1, page_size):
            res = self.get_word(self.resolved_word_url, page)
            words += res['words']
        return words

    def add_word(self, words):
        for words in split(words,10):
            url = 'https://www.shanbay.com/bdc/vocabulary/add/batch/'
            self.headers['Referer'] = 'https://www.shanbay.com/bdc/vocabulary/add/batch/'
            res = requests.request("GET", url, headers=self.headers, params={
                "words": words, "_": "1530021937223"})
            res = json.loads(res.text)
            print(len(res['learning_dicts']))
        pass


def get_word_from_file(path):
    word = map(lambda w: w.strip(), open(path).readlines())
    return list(set(word))

def split(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arrs

config = {
    'userid': '109630519',
    'sessionid': '".eJyrVopPLC3JiC8tTi2KT0pMzk7NS1GyUkrOz83Nz9MDS0FFi_V885Myc1J98tMz85ygKnWQtWcCdRoaWJoZG5gaWtYCAPwCIBI:1fXThC:43Q0qBbtrd5DcNKaS40khdb_WjY"',
    'auth_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1vYmlsZV80MTZhMWVmZTY0IiwiZGV2aWNlIjowLCJpc19zdGFmZiI6ZmFsc2UsImlkIjoxMDk2MzA1MTksImV4cCI6MTUzMDg4NTY2N30.5ykh7hD85e5a0I0e5jfOwaM33L0fmNIGSzUgzHkJkJc'
}
api = Shanbay(config)
api.add_word(get_word_from_file('./unknow.data'))
