# -*- coding: utf-8 -*-
"""
Author: HuangZehong
Created Time: 2024/04/25
Last Edited Time: 2024/04/25
"""
import json
import time
from datetime import datetime, timedelta
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Ticket:
    def __init__(self, args) -> None:
        self.url = args.url
        self.username = args.username
        self.password = args.password
        self.campus = args.campus
        self.sport = args.sport
        self.method = args.method  # 预约方式
        self.date = args.date  # 预约日期
        self.time = args.time  # 预约时间段
        self.venue = args.venue  # 选择场地
        self.wait_time = 10

        # 放票时间是前一天中午12:30
        year, month, day = [int(item) for item in self.date.split('-')]
        self.target_time = datetime(year, month, day, 12, 30) - timedelta(days=1)
        logging.info(f"放票时间是{self.target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.driver = webdriver.Chrome()
        self.cfg = read_json('./config.json')
    
    def start(self) -> False:
        # 打开网址
        logging.info(f'打开网址：{self.url}')
        self.driver.get(self.url)
        # 登录
        self.login()
        # 等待放票
        self.wait()
        
        # 开始抢票
        # 100: 还未放票
        # 200: 抢到票，但未支付
        # 201: 抢到票并成功支付
        # 400: 没抢到票
        # 401: 抢到票，但是支付失败
        logging.info('开始抢票')
        code = self.book()
        while code == '100':
            logging.info('还未放票，刷新重试')
            self.driver.refresh()
            code = self.book()
            
        if code == '200':  # 抢到票，支付订单
            code = self.pay()
        
        return code
    
    def login(self) -> None:
        logging.info('登录中')
        # 输入账号
        self.driver.find_element(by=By.ID, value='username').click()
        self.driver.find_element(by=By.ID, value='username').clear()
        self.driver.find_element(by=By.ID, value='username').send_keys(self.username)
        # 输入密码
        self.driver.find_element(by=By.ID, value='password').click()
        self.driver.find_element(by=By.ID, value='password').clear()
        self.driver.find_element(by=By.ID, value='password').send_keys(self.password)
        # 回车登录
        self.driver.find_element(by=By.ID, value='password').send_keys(Keys.ENTER)
        logging.info('成功登录')
    
    def wait(self) -> None:
        """等到放票前10秒开始抢票"""
        now = datetime.now()
        time_diff = (self.target_time - now).total_seconds()
        if time_diff > 10:
            # 放票前5秒开始抢
            logging.info(f'距离放票时间还有{time_diff}秒，等待放票中...')
            time.sleep(time_diff - 10)
    
    def book(self) -> str:
        # 选择校区 ================================================================
        WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='bh-btn bh-btn-primary']"))
        )  # 等待页面加载
        buttons = self.driver.find_elements(By.XPATH, "//div[@class='bh-btn bh-btn-primary']")  # 定位元素
        for button in buttons:
            if button.text == self.campus:  # 点击对应校区
                button.click()
                break
        else:
            raise ValueError(f'校区不存在：{self.campus}')
        logging.info(f'{self.campus}')
        
        # 选择体育项目 ================================================================
        WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='frame-5']"))
        )  # 等待页面加载
        buttons = self.driver.find_elements(By.XPATH, "//div[@class='frame-5']")  # 定位元素
        # 点击对应体育项目
        idx = self.cfg['sport'][self.sport]['id']
        buttons[idx].click()
        logging.info(f'{self.sport}')
        
        # 选择预约方式 ================================================================
        # TODO
        
        # 选择日期 ================================================================
        WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//label[@for='{self.date}']"))
        )  # 等待页面加载
        buttons = self.driver.find_elements(By.XPATH, f"//label[@for='{self.date}']")  # 定位元素
        if len(buttons) == 0:  # 还未放票
            return '100'
        else:  # 点击对应日期
            buttons[0].click()
        logging.info(f'{self.date}')
        
        # 选择时间段 ================================================================
        if self.driver.find_elements(By.XPATH, f"//label[@for='{self.time}']/div[@class='ellipse']"):
            # 没票了
            logging.info('该场次已满员或已过期！')
            return '400'
        self.driver.find_elements(By.XPATH, f"//label[@for='{self.time}']")[0].click()
        logging.info(f'{self.time}')
        
        # 选择场地 ================================================================
        buttons = self.driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'rectangle-3')]/div[contains(@class, 'group-2')]/label/div[contains(@class, 'frame-child1')]"
        )
        if self.venue == '':  # 没有指定场地，抢任意场地即可
            if len(buttons) == 0:
                # 没票了
                logging.info('该场次已满员！')
                return '400'
            buttons[0].click()
        else:  # 指定了场地
            for button in buttons:
                if self.venue in button.text:
                    button.click()
                    break
            else:
                logging.info('该场次已满员！')
                return '400'
        
        # 提交预约 ================================================================
        self.driver.find_elements(By.XPATH, "(//button[@class='bh-btn bh-btn-default bh-btn-large'])")[1].click()
        logging.info(f'预约成功！')
        
        return '200'
    
    def pay(self) -> str:
        # TODO
        ...
        

def read_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    return obj
