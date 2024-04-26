# SZU体育场馆抢票
由于SZU体育场馆抢票激烈，部分场馆一票难求，故创建该项目尝试用脚本自动抢票，作为一个python实践学习项目。

## 免责声明
该项目仅用于python学习，禁止用于真实抢票，违反学校规定者请自行承担后果。

## 环境
电脑需要有谷歌浏览器

python版本3.10

安装依赖包：
```shell
pip install -r requirements.txt
```

## 使用方式
输入个人信息和要抢票的场次后，运行脚本，程序会一直等待至放票前的10秒钟，然后开始自动抢票。可以提前运行程序挂着，到点自动抢票。
1. 命令行运行
    ```shell
    python run.py --username [username] --password [password] --pay_password [pay_password] --campus [campus] --sport [sport] --date [date] --time [time] --venue [venue]
    ```
    各个参数的含义：
    - username: 学号
    - password: 登陆密码
    - pay_password: 支付密码
    - campus: 校区，“粤海校区”或“丽湖校区”
    - sport: 体育项目
    - date: 预约日期
    - time: 预约时间段
    - venue: 场地，不指定则会自动抢任意空闲场地，建议不要指定场地

    示例：抢24年4月26日21点至22点场次的粤海校区排球场
    ```shell
    python run.py --username 2024888888 --password 88888888 --pay_password 666666 --campus 粤海校区 --sport 排球 --date 2024-04-26 --time 21:00-22:00
    ```

2. IDE运行python脚本

    将run.py文件中的parse_args函数中各个参数的默认值修改成对应信息，运行run.py脚本