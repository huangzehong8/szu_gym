# -*- coding: utf-8 -*-
"""
Author: HuangZehong
E-Mail: zh.huang8.cn@gmail.com
Created Time: 2024/04/25
Last Edited Time: 2024/04/26
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
        self.pay_password = args.pay_password
        
        self.campus = args.campus  # 校区
        self.sport = args.sport  # 体育项目
        self.method = args.method  # 预约方式
        self.date = args.date  # 预约日期
        self.time = args.time  # 预约时间段
        self.venue = args.venue  # 选择场地
        self.wait_time = 10  # 等待页面加载的时间

        # 放票时间是前一天中午12:30
        year, month, day = [int(item) for item in self.date.split('-')]
        self.target_time = datetime(year, month, day, 12, 30) - timedelta(days=1)
        logging.info(f"目标场次的放票时间：{self.target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.driver = webdriver.Chrome()
    
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
        # 101: 没抢到票，尝试抢其余票
        # 200: 抢到票，但未支付
        # 201: 抢到票并成功支付
        # 400: 没抢到票，全部没票了
        # 401: 抢到票，但是支付失败
        logging.info('开始抢票...')
        code = self.book()
        while code == '100' or code == '101':
            logging.info('刷新重试...')
            self.driver.refresh()
            code = self.book()
            
        if code == '200':  # 抢到票，支付订单
            code = self.pay()
        
        return code
    
    def login(self) -> None:
        logging.info(f'{self.username}登录中')
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
        logging.info(f'{self.username}成功登录')
    
    def wait(self) -> None:
        """等到放票前10秒开始抢票"""
        now = datetime.now()
        time_diff = (self.target_time - now).total_seconds()
        if time_diff > 10:
            # 放票前5秒开始抢
            logging.info(f'距离放票时间还有{time_diff}秒，等待放票中...')
            time.sleep(time_diff - 10)
    
    def book(self) -> str:
        logging.info(f'选择校区：{self.campus}')
        # 选择校区 ================================================================
        WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='bh-btn bh-btn-primary']"))
        )  # 等待页面加载
        self.driver.find_element(By.XPATH, f"//div[text()='{self.campus}']").click()  # 点击对应校区
        
        # 选择体育项目 ================================================================
        logging.info(f'选择体育项目：{self.sport}')
        WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='frame-5']"))
        )  # 等待页面加载
        if button := self.driver.find_elements(By.XPATH, f"//div[text()='{self.sport}']"):
            button[0].click()  # 点击对应体育项目
        else:  # 当前页面没有找到目标体育项目
            self.driver.find_element(By.XPATH, f"//div[@class='group-14']").click()  # 切换到下一页
            self.driver.find_element(By.XPATH, f"//div[text()='{self.sport}']").click()  # 点击对应体育项目
        
        # 选择预约方式 ================================================================
        # TODO: 选择散场或包场。目前只能默认选项。
        # logging.info(f'选择预约方式：{self.method}')
        
        # 选择日期 ================================================================
        logging.info(f'选择预约日期：{self.date}')
        WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//label[@for='{self.date}']"))
        )  # 等待页面加载
        buttons = self.driver.find_elements(By.XPATH, f"//label[@for='{self.date}']")  # 定位元素
        if len(buttons) == 0:  # 还未放票
            logging.info('还未放票！')
            return '100'
        else:  # 点击对应日期
            buttons[0].click()
        
        # 选择时间段 ================================================================
        logging.info(f'选择预约时间段：{self.time}')
        if self.driver.find_elements(By.XPATH, f"//label[@for='{self.time}']/div[@class='ellipse']"):
            # 没票了
            logging.warning('该场次已满员或已过期！')
            return '400'
        self.driver.find_elements(By.XPATH, f"//label[@for='{self.time}']")[0].click()
        
        # 选择场地 ================================================================
        logging.info(f'选择场地：{self.venue if self.venue != "" else "任意"}')
        buttons = self.driver.find_elements(
            By.XPATH, '//*[@id="apply"]/div[3]/div[10]/div/label/div[contains(text(),"可预约")]'
        )
        if self.venue == '':  # 没有指定场地，抢任意场地即可
            if len(buttons) == 0:
                # 没票了
                logging.warning('该场次已满员！')
                return '400'
            buttons[0].click()
        else:  # 指定了场地
            for button in buttons:
                if self.venue in button.text:
                    button.click()
                    break
            else:
                logging.warning('该场次已满员！')
                return '400'
        
        # 提交预约 ================================================================
        logging.info(f'提交预约中...')
        self.driver.find_elements(By.XPATH, "//button[@class='bh-btn bh-btn-default bh-btn-large']")[1].click()
        WebDriverWait(self.driver, self.wait_time).until(
            EC.any_of(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='bh-dialog-exceptBtn-con bh-dialog-icon-colorwarning']")),
                EC.visibility_of_element_located((By.XPATH, "//a[text()='取消预约']"))
            )
        )
        if self.driver.find_elements(By.XPATH, "//div[@class='bh-dialog-exceptBtn-con bh-dialog-icon-colorwarning']"):
            logging.warning(f'预约失败！')
            return '101'
        elif self.driver.find_elements(By.XPATH, "//a[text()='取消预约']"):
            logging.info(f'预约成功！')
            return '200'
        else:
            raise ValueError('提交预约错误')
    
    def pay(self) -> str:
        logging.info('支付订单中...')
        # 点击“未支付”
        button = WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[text()='未支付']"))
        )
        button.click()
        WebDriverWait(self.driver, self.wait_time).until(
            EC.visibility_of_element_located((By.XPATH, f"//div[@class='jqx-rc-all jqx-window jqx-popup jqx-widget jqx-widget-content']"))
        )
        
        # 三种支付方式
        if button := self.driver.find_elements(By.XPATH, "//button[text()='(剩余金额)支付']"):
            logging.info('支付方式：剩余金额支付')
            button[0].click()
            if self.driver.find_elements(By.XPATH, "//div[text()='支付成功']"):
                logging.info('支付成功！')
                return '201'
            else:
                logging.warning('支付失败！')
                return '401'
            
        elif button := self.driver.find_elements(By.XPATH, "//button[text()='(体育经费)支付']"):
            logging.info('支付方式：体育经费支付')
            button[0].click()
             # 跳转到新的窗口
            window_handles = self.driver.window_handles  # 获取所有窗口句柄
            self.driver.switch_to.window(window_handles[-1])  # 切换到最新窗口
            WebDriverWait(self.driver, self.wait_time).until(EC.element_to_be_clickable((By.ID, "btnNext"))).click()  # 点击“下一步”
            WebDriverWait(self.driver, self.wait_time).until(EC.element_to_be_clickable((By.ID, "password"))).click()  # 点击“密码框”
            # 输入密码
            for c in self.pay_password:
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, f"key-{c}"))).click()
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, f"key-11"))).click()  # 点击“确定”
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "qrbtn"))).click()  # 确认支付
            # 检查
            if self.driver.current_url.endswith('myBooking'):
                logging.info('支付成功！')
                return '201'
            else:
                logging.warning('支付失败！')
                return '401'
            
        elif button := self.driver.find_elements(By.XPATH, "//button[text()='(校园卡)支付']"):
            # TODO
            raise ValueError('预期的支付方式不存在')
            
        else:
            raise ValueError('预期的支付方式不存在')
            

def read_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    return obj
