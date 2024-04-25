# -*- coding: utf-8 -*-
"""
Author: HuangZehong
Created Time: 2024/04/24
Last Edited Time: 2024/04/25
"""
import time
from datetime import datetime
from dataclasses import dataclass, field
import logging

from gym_ticket import Ticket


@dataclass
class UserInfo:
    url: str = field(default='https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do?t_s=1713928760905#/sportVenue')
    username: str = field(default='2210433011')
    password: str = field(default='08211212')
    payment_password: str = field(default='211212')
    
    campus: str = field(default='粤海校区')
    sport: str = field(default='二楼有氧健身')
    method: str = field(default='散场')
    date: str = field(default='2024-04-26')
    time: str = field(default='08:00-09:00')
    venue: str = field(default='二楼健身房')


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    args = UserInfo()
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
    