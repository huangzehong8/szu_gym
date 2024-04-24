import json
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = 'https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do?t_s=1713928760905#/sportVenue'


def main():
    with open('./config.json', 'r') as f:
        cfg = json.load(f)
    print(cfg)
    
    driver = webdriver.Chrome()
    driver.get(url)
    
    # 登录
    driver.find_element(by=By.ID, value='username').click()
    driver.find_element(by=By.ID, value='username').clear()
    driver.find_element(by=By.ID, value='username').send_keys(cfg['username'])
    driver.find_element(by=By.ID, value='password').click()
    driver.find_element(by=By.ID, value='password').clear()
    driver.find_element(by=By.ID, value='password').send_keys(cfg['password'])
    driver.find_element(by=By.ID, value='password').send_keys(Keys.ENTER)
    
    # 点击“粤海校区”
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='bh-btn bh-btn-primary'])")))
    buttons = driver.find_elements(By.XPATH, "(//div[@class='bh-btn bh-btn-primary'])")
    buttons[0].click()
    
    # 点击“一楼重量型健身”
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='frame-5'])")))
    buttons = driver.find_elements(By.XPATH, "(//div[@class='frame-5'])")
    buttons[7].click()
    
    # 选择日期、时间、场地
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//label[@for='{cfg['date']}']")))
    driver.find_elements(By.XPATH, f"//label[@for='{cfg['date']}']")[0].click()
    driver.find_elements(By.XPATH, f"//label[@for='{cfg['time']}']")[0].click()
    # driver.find_elements(By.XPATH, "//label[@for='312801690c364d2cb56df744a39f38f1']")[0].click()
    driver.find_elements(By.XPATH, "//label[@for='e74cd398ae334edb9fb1f707bae00cd9']")[0].click()
    
    # 提交预约
    buttons = driver.find_elements(By.XPATH, "(//button[@class='bh-btn bh-btn-default bh-btn-large'])")
    buttons[1].click()
    
    # 支付
    # 点击“未支付”
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'j-row-pay')]")))
    buttons = driver.find_elements(By.XPATH, "//a[contains(@class, 'j-row-pay')]")
    buttons[0].click()
    # 点击“体育经费支付”
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "(//button[@class='bh-btn bh-btn-primary bh-pull-right'])")))
    buttons = driver.find_elements(By.XPATH, "(//button[@class='bh-btn bh-btn-primary bh-pull-right'])")
    buttons[0].click()
    # 跳转到新的窗口
    window_handles = driver.window_handles  # 获取所有窗口句柄
    driver.switch_to.window(window_handles[-1])  # 切换到最新窗口
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btnNext"))).click()  # 点击“下一步”
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "password"))).click()  # 点击“密码框”
    # 输入密码
    for c in cfg['pay_password']:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, f"key-{c}"))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, f"key-11"))).click()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "qrbtn"))).click()  # 确认支付
    
    time.sleep(10)


if __name__ == '__main__':
    main()
    