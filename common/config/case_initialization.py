import json
import requests,re
from common.config.loger import loger
from common.config.path_utils import config


#环境获取
environment_path = config['environment']['environment']
environment_url = config['environment'][environment_path + '_url']
environment_Authorization = config['environment'][environment_path + '_Authorization']
#清除购物车
headers = {
        "Content-Type": "application/json",
        "CHANNEL_ID": "manual",
        "Authorization": environment_Authorization
    }

def case_shop_cart():
    ada = log_ada()
    data = {
        "discountPercentage": 0,
        "consignAda": ada,
        "loginAda": ada,
        "loginType": 'PC',
        "loginMemberType": 'PC',
        "type": 0,
        "channelCode": "INT"
    }
    response = requests.post(
        f"{environment_url}trading-cart/v1/api/cart/clean-cart",
        headers=headers,
        data=json.dumps(data)
    )
    print(response.json())
    return response.json()
def sql_ada(phone):
    data = {
        "channelId": "wechatframework",
        "phoneNumber": phone
    }
    response = requests.post(
        f"{environment_url}login-center/api/v6/queryBindByPn",
        headers=headers,
        data=json.dumps(data)
    )
    return response.json()
def log_ada():
    script_log = loger.logs
    pattern = re.compile(r"步骤:\d+-输入操作-账号输入:{'value': '([^']+)', 'sleep': (\d+)}")
    for log_entry in script_log:
        match = pattern.search(log_entry)
        if match:
            ada = match.group(1)
            sleep_time = match.group(2)
            if len(ada) == 11 and ada[0:1] == '1':
                ada = sql_ada(ada)
                adas = ada['data']['ada']
                return adas
            else:
                return ada
    else:

        print("未找到账号输入的数据.")
