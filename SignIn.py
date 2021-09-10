# -*- coding: UTF-8 -*-
# Desc: 和彩云自动打卡签到 gen: SCF-GENERATE
# Time: 2020/02/20 12:53:28
# Auth: xuthus
# SIG: QQ Group(824187964)

import os
import json
from urllib import parse

import requests

OpenLuckDraw = True if os.getenv("LUCK_DRAW") == 'true' else False  # 是否开启自动幸运抽奖(首次免费, 第二次5积分/次) 不建议开启 否则会导致多次执行时消耗积分
BARK_TOKEN = os.environ['BARK_TOKEN']  # BARK Token
Cookie = os.environ['COOKIE']  # 抓包Cookie
Referer = os.environ['REFERER']  # 抓包referer
UA = "Mozilla/5.0 (Linux; Android 10; M2007J3SC Build/QKQ1.191222.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 MCloudApp/7.6.0"

# BARK
def bark_push(title, content):
    print(title+"\n"+content)
    if not BARK_TOKEN:
        print("bark服务的bark_token未设置!!\n取消推送")
        return
    print("bark服务启动")
    try:
        response = requests.get('''https://api.day.app/{0}/{1}/{2}'''.format(BARK, title, quote_plus(content))).json()
        if response['code'] == 200:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(e)
        print('Bark推送失败！')
        
               
def getEncryptTime():
    target = "http://caiyun.feixin.10086.cn:7070/portal/ajax/tools/opRequest.action"
    headers = {
        "Host": "caiyun.feixin.10086.cn:7070",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://caiyun.feixin.10086.cn:7070",
        "Referer": Referer,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": Cookie,
    }
    payload = parse.urlencode({
        "op": "currentTimeMillis"
    })
    resp = json.loads(requests.post(target, headers=headers, data=payload).text)
    if resp['code'] != 10000:
        print('获取时间戳失败: ', resp['msg'])
        return 0
    return resp['result']


def getTicket():
    target = "https://hecaiyun.vercel.app/api/10086_calc_sign"
    payload = {
        "sourceId": 1003,
        "type": 1,
        "encryptTime": getEncryptTime()
    }
    resp = json.loads(requests.post(target, data=payload).text)
    if resp['code'] != 200:
        print('加密失败: ', resp['msg'])
    return resp['data']


def luckDraw():
    target = "http://caiyun.feixin.10086.cn:7070/portal/ajax/common/caiYunSignIn.action"
    headers = {
        "Host": "caiyun.feixin.10086.cn:7070",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://caiyun.feixin.10086.cn:7070",
        "Referer": Referer,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": Cookie,
    }
    payload = parse.urlencode({
        "op": "luckDraw",
        "data": getTicket()
    })

    resp = json.loads(requests.post(target, headers=headers, data=payload).text)

    if resp['code'] != 10000:
        print('自动抽奖失败: ', resp['msg'])
        return '自动抽奖失败: ' + resp['msg']
    else:
        if resp['result']['type'] == '40160':
            return '自动抽奖成功: 小狗电器小型手持床铺除螨仪'
        elif resp['result']['type'] == '40175':
            return '自动抽奖成功: 飞科男士剃须刀'
        elif resp['result']['type'] == '40120':
            return '自动抽奖成功: 京东京造电动牙刷'
        elif resp['result']['type'] == '40140':
            return '自动抽奖成功: 10-100M随机长期存储空间'
        elif resp['result']['type'] == '40165':
            return '自动抽奖成功: 夏新蓝牙耳机'
        elif resp['result']['type'] == '40170':
            return '自动抽奖成功: 欧莱雅葡萄籽护肤套餐'
        else:
            return '自动抽奖成功: 谢谢参与'


def run():
    target = "http://caiyun.feixin.10086.cn:7070/portal/ajax/common/caiYunSignIn.action"
    headers = {
        "Host": "caiyun.feixin.10086.cn:7070",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://caiyun.feixin.10086.cn:7070",
        "Referer": Referer,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": Cookie,
    }

    ticket = getTicket()
    payload = parse.urlencode({
        "op": "receive",
        "data": ticket,
    })

    resp = json.loads(requests.post(target, headers=headers, data=payload).text)
    if resp['code'] != 10000:
        bark_push('和彩云签到', '失败:' + resp['msg'])
    else:
        content = '签到成功\n月签到天数:' + str(resp['result']['monthDays']) + '\n总积分:' + str(
            resp['result']['totalPoints'])
        if OpenLuckDraw:
            content += '\n\n' + luckDraw()
        bark_push('和彩云签到', content)


def main_handler(event, context):
    run()


# 本地测试
if __name__ == '__main__':
    run()
