# -*- coding:utf-8 -*-
"""
@author:lee
@file: login.py
@time: 2019/11/08 21:28
"""
import os

import requests
import tesserocr
from PIL import Image
from bs4 import BeautifulSoup

from url import URL


class Course:
    def __init__(self, username, password):
        requests.packages.urllib3.disable_warnings()
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.get(URL.index_url)
        # post参数
        self.post_data = {}
        self.user_agent = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome\
        /71.0.3578.98 Safari/537.36'''
        self.modulus = ''
        self.exponent = ''

    # 获取验证码
    def get_check_code(self):
        yzm_header = {
            'User-Agent': self.user_agent
        }
        y_res = self.session.get(URL.captcha_url, headers=yzm_header)
        with open('check.png', 'wb') as f:
            f.write(y_res.content)
        print('成功获取验证码')
        return y_res.content

    # 实现加密算法
    @staticmethod
    def encrypt(modulus, exponent):
        public_modulus = int(modulus, 16)
        public_exponent = int(exponent, 16)

        def cipher(text):
            # Beware, plaintext must be short enough to fit in a single block!
            plaintext = int(text[::-1].encode("utf-8").hex(), 16)
            res = pow(plaintext, public_exponent, public_modulus)
            # return hex representation
            return '%x' % res

        return cipher

    # 获取加密相关参数
    def get_security(self):
        s_headers = {
            'User-Agent': self.user_agent,
        }
        res = self.session.get(URL.get_key_url, headers=s_headers)
        self.modulus = res.json()['modulus']
        self.exponent = res.json()['exponent']

    # 构造密码
    def structure_password(self):
        self.get_security()
        self.password = self.encrypt(self.modulus, self.exponent)(self.password)

    # 构造post数据
    def structure_post_data(self):
        # 获取验证码
        self.get_check_code()
        # 加密
        self.structure_password()
        self.post_data['username'] = self.username
        self.post_data['password'] = self.password

        self.post_data["_eventId"] = 'submit'
        self.post_data["geolocation"] = ''

    # 登录
    def login(self, r):
        # 处理验证码
        self.structure_post_data()
        self.deal_code()
        self.post_data["execution"] = 'e1s' + r
        captcha = self.dist_captcha_code().replace('\n', '')
        # print('={}='.format(captcha.replace('\n', '')))
        print('正在识别验证码...')
        self.post_data["captcha"] = str(captcha).replace(' ', '')
        self.session.post(URL.auth_server_url, data=self.post_data)

    # 处理验证码图片
    @staticmethod
    def deal_code():
        img = Image.open('check.png').convert('L')
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if img.getpixel((x, y)) < 30:
                    img.putpixel((x, y), 255)
                if (img.getpixel((x, y)) > 30) and img.getpixel((x, y)) < 230:
                    img.putpixel((x, y), 0)
        img.save('code.png')

    # 识别验证码
    @staticmethod
    def dist_captcha_code():
        img = Image.open('code.png')
        img_l = img.convert('L')
        threshold = 180
        table = []
        for j in range(256):
            if j < threshold:
                table.append(0)
            else:
                table.append(1)
        image = img_l.point(table, '1')
        return tesserocr.image_to_text(image)

    # 爬取并解析理论课课表
    def theory_course(self):
        self.session.get(URL.jwc_auth_url)
        self.session.get(URL.theory_course_index, verify=False, allow_redirects=True)
        res = self.session.get(URL.theory_course_detail, verify=False, allow_redirects=True)
        data_soup = BeautifulSoup(res.text, 'html.parser')
        data_soup = BeautifulSoup(str(data_soup.find_all(attrs={'id': 'choosenCourseTable'})), 'html.parser')
        data_tbody = BeautifulSoup(str(data_soup.tbody), 'html.parser')
        data_trs = data_tbody.select('tr')
        trs = []
        for tds in data_trs:
            data_tds = BeautifulSoup(str(tds), 'html.parser').select('td')
            tds = []
            for td in data_tds:
                tds.append(td)
            trs.append(tds)
        if os.path.exists('course.txt'):
            os.remove('course.txt')
        k = 1
        for i in trs:
            for j in range(len(i)):
                if BeautifulSoup(str(i[j]), 'html.parser').text:
                    res = BeautifulSoup(str(BeautifulSoup(str(i[j]), 'html.parser').select('span')), 'html.parser').text
                    if len(res) > 5:
                        # print(str(j-1), str(k), res)
                        with open('course.txt', 'a+') as f:
                            f.write(str(j - 1) + '\t' + str(k) + '\t' + res + '\n')
            k += 1

    # 爬取实验课课表
    def experiment_course(self):
        auth_info = self.session.get(URL.syk_auth_url, verify=False, allow_redirects=True)
        auth_info = auth_info.text.split('\'')[1]
        self.session.get(URL.syk_url, verify=False, allow_redirects=True)
        self.session.get(URL.syk_detail + auth_info, allow_redirects=True, verify=False)
        detail = self.session.get(URL.experiment_url)
        self.resolve_experiment_course(detail)
        page = 2
        while True:
            try:
                data = {'currYearterm': '2019-2020-1', 'currTeachCourseCode': '%', 'page': page}
                res = self.session.post(URL.experiment_url, data=data)
                flag = self.resolve_experiment_course(res)
                page += 1
                if not flag:
                    break
            except:
                break

    # 解析实验课课表
    @staticmethod
    def resolve_experiment_course(html):
        detail = BeautifulSoup(html.text, 'html.parser')
        detail_course = detail.find_all(attrs={'class': 'table1'})
        detail_course = BeautifulSoup(str(detail_course[1]), 'html.parser')
        trs = detail_course.select('tr')
        content = []
        for i in range(1, len(trs)):
            tds = []
            item = BeautifulSoup(str(trs[i]), 'html.parser').select('td')
            for j in item:
                tds.append(BeautifulSoup(str(j), 'html.parser').text)
            content.append(tds)
        for k in content:
            with open('course.txt', 'a+') as f:
                f.write(str(k) + '\n')
        return len(content[0])

    # 爬取并解析成绩
    def get_score(self):
        res = self.session.post(URL.score_url)
        res = res.json()
        res = res['body']['result']
        res = res.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
        res = res.split(',')
        score = []
        for item in res:
            score.append(item.split(':'))
        k = 0
        with open('score.txt', 'w+') as f:
            f.write('{0:<10}'.format('term'))
            f.write('{0:<10}'.format('credit'))
            f.write('{0:<10}'.format('catalog'))
            f.write('{0:{1}<25}'.format('course', chr(12288)))
            f.write('{0:<10}'.format('scroll'))
            f.write('\n')
            for i in score:
                if k % 5 == 3:
                    f.write('{0:{1}<25}'.format(i[1].strip('"'), chr(12288)))
                else:
                    f.write('{0:<10}'.format(i[1].strip('"')))
                k += 1
                if k % 5 == 0:
                    f.write('\n')

    # 爬取并解析考试信息
    def get_exam(self):
        res = self.session.get(URL.exam_url)
        res = BeautifulSoup(res.text, 'html.parser')
        res = res.find_all(attrs={'id': 'finalExamTable'})
        trs = BeautifulSoup(str(res), 'html.parser').select('tr')
        exam = []
        for item in trs:
            inner = []
            tds = BeautifulSoup(str(item), 'html.parser').select('td')
            for k in tds:
                inner.append(BeautifulSoup(str(k), 'html.parser').text)
            exam.append(inner)
        with open('exam.txt', 'w+') as f:
            for e in exam:
                f.write(str(e) + '\n')


while True:
    t = Course('5120173525', 'lcg961835'[::-1])
    print('正在登录...')
    try:
        t.login(str(1))
        print('验证码识别成功...')
        t.theory_course()
        print('爬取理论课成功...')
        t.experiment_course()
        print('爬取实验课成功...')
        t.get_score()
        print('爬取成绩成功...')
        t.get_exam()
        print('爬取考试信息成功...')
        break
    except:
        print('爬取失败...')
