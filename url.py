# -*- coding:utf-8 -*-
"""
@author:lee
@file: url.py
@time: 2019/11/08 21:29
"""


class URL:
    # 认证
    auth_server_url = "http://cas.swust.edu.cn/authserver/login?service="
    # 服务平台登录页
    index_url = auth_server_url + 'http://my.swust.edu.cn/mht_shall/a/service/serviceFrontManage/cas'
    # 教务处首页
    jwc_auth_url = auth_server_url + "https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?\
    event=studentPortal:DEFAULT_EVENT"
    # 实验课首页
    syk_auth_url = auth_server_url + "http://202.115.175.177/swust/"
    # 验证码地址
    captcha_url = 'http://cas.swust.edu.cn/authserver/captcha'
    # 获取加密信息
    get_key_url = 'http://cas.swust.edu.cn/authserver/getKey'
    # 理论课首页
    theory_course_index = "https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:DEFAULT_EVENT"
    # 理论课课表
    theory_course_detail = 'https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:courseTable'
    # 实验课
    experiment_url = 'http://202.115.175.177/StuExpbook/book/bookResult.jsp'
    # 成绩
    score_url = 'http://my.swust.edu.cn/mht_shall/a/service/studentMark'
    # 考试
    exam_url = 'https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:examTable'
    student_info_url = 'http://my.swust.edu.cn/mht_shall/a/service/studentInfo'
    kebiao_url = 'https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:courseTable'
    syk_url = 'http://202.115.175.177/StuExpbook/login.jsp'
    syk_detail = 'http://202.115.175.177'
