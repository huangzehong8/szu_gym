# -*- coding: utf-8 -*-
"""
Author: HuangZehong
E-Mail: zh.huang8.cn@gmail.com
Created Time: 2024/04/24
Last Edited Time: 2024/04/26
"""
import time
import argparse
from datetime import datetime
from dataclasses import dataclass, field, fields
import logging

from gym_ticket import Ticket


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    args = parse_args()
    logging.info(args)
    
    ticket = Ticket(args=args)
    wait(ticket.target_time)
    code = ticket.start()
    if code == '201':
        logging.info('恭喜你！抢票成功！')
    elif code == '400':
        logging.info('很抱歉，未抢到票！')
    elif code == '401':
        logging.info('抢到票但未成功支付，请尽快手动支付！')
    else:
        raise ValueError(f'状态码异常: {code}')


def parse_args():
    parser = argparse.ArgumentParser(description='SZU_GYM')
    parser.add_argument('-u', '--url', type=str, default='https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do?t_s=1713928760905#/sportVenue', help='SZU预定体育场馆的网址')
    parser.add_argument('-U', '--username', type=str, default='', help='学号')
    parser.add_argument('-P', '--password', type=str, default='', help='登陆密码')
    parser.add_argument('-p', '--pay_password', type=str, default='', help='支付密码')
    parser.add_argument('-c', '--campus', type=str, default='粤海校区', help='校区，“粤海校区”或“丽湖校区”')
    parser.add_argument('-s', '--sport', type=str, default='排球', help='体育项目')
    parser.add_argument('-m', '--method', type=str, default='', help='预约方式，此参数暂时无效，无需指定')
    parser.add_argument('-d', '--date', type=str, default='2024-04-26', help='预约日期')
    parser.add_argument('-t', '--time', type=str, default='21:00-22:00', help='预约时间段')
    parser.add_argument('-v', '--venue', type=str, default='', help='场地，不指定则会自动抢任意空闲场地，建议不要指定场地')
    _args = parser.parse_args()
    args = UserInfo()
    for f in fields(UserInfo):
        if f.name in _args:
            setattr(args, f.name, getattr(_args, f.name))
    return args


@dataclass
class UserInfo:
    url: str = field(default='https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do?t_s=1713928760905#/sportVenue')
    username: str = field(default='xxxxxxxxxx')  # 学号
    password: str = field(default='xxxxxxxxxx')  # 登录密码
    pay_password: str = field(default='xxxxxxxxxx')  # 支付密码
    
    campus: str = field(default='粤海校区')  # 校区
    sport: str = field(default='排球')  # 体育项目
    method: str = field(default='')  # TODO: 此参数暂时无效，无需指定
    date: str = field(default='2024-04-26')  # 预约日期
    time: str = field(default='21:00-22:00')  # 预约时间段
    venue: str = field(default='')  # 场地，不指定则会自动抢任意空闲场地，建议不要指定场地
    

def wait(target_time: datetime) -> None:
    """等到放票前1分钟再登录网站"""
    now = datetime.now()
    time_diff = (target_time - now).total_seconds()
    if time_diff > 60:
        # 放票前5秒开始抢
        logging.info(f'距离放票时间还有{time_diff / 60}分钟，等待放票中...')
        time.sleep(time_diff - 60)
    logging.info('准备开始抢票')


if __name__ == '__main__':
    main()
    