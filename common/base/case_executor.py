import os,time,json
import csv,re
import json,sys
from common.base.utils_json import process_test_case
from common.base.basic import *
from datetime import datetime
from common.config.path_utils import phico_path,grandparent_directory,name_code
from common.config.loger import loger




def execute_open_weixin(driver, details, action_detail=None):
    sleep = details.get('sleep')
    start_weixin(driver, sleep)


    loger.log("打开微信-{}:{}".format(action_detail, details))


def execute_click(driver, details, action_detail=None):
    element = details.get('locator')
    sleep = details.get('sleep')
    path = details.get('type')
    instance = details.get('instance')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    click_result = element_click(driver, path, element, sleep, instance)
    if click_result is False:
        loger.error("点击操作-{}:{}".format(action_detail, details))
        shot_png(driver, action_detail)
        sys.exit(1)
    else:
        loger.log("点击操作-{}:{}".format(action_detail, details))


def execute_input(driver, details, action_detail=None):
    value = details.get('value')
    sleep = details.get('sleep')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    key_result = send_key(driver, value, sleep)
    if key_result is False:
        loger.error("输入操作-{}:{}".format(action_detail, details))
        shot_png(driver, action_detail)
        sys.exit(1)
    else:
        loger.log("输入操作-{}:{}".format(action_detail, details))


def execute_assertion(driver, details, action_detail=None):
    if '|' in details.get('value', '') and '.csv' in details.get('value'):
        # 调用 process_csv_in_details
        process_csv_in_details(details)
    if '|' in details.get('locator', '') and '.csv' in details.get('locator'):
        # 调用 process_csv_in_details
        process_csv_in_details(details)

    if 'value' in details:
        element = details.get('locator')
        sleep = details.get('sleep')
        type = details.get('type')
        instance = details.get('instance')
        sibling = details.get('sibling')
        #details['value'] = remove_newAccount(details['value'])
        wait_until_element_disappears(driver)
        dump_hierarchy(driver)
        if sibling:
            actual_value = payment_element_order(driver, element, instance)
        else:
            actual_value = element_find(driver, type, element, sleep, instance)
        # 如果找到了文本值或者是布尔值，进行处理
        if isinstance(actual_value, (str, bool, int)):
            #actual_value_str = str(actual_value).replace("：", ":")
            actual_value_str = str(actual_value).strip().replace("：", ":")
        else:
            loger.error(f"获取到的actual_value类型不受支持: {type(actual_value)}")
            actual_value_str = ""
        expected_value_str = str(details.get('value')).replace("：", ":")

        if actual_value_str != expected_value_str:
            loger.error(f"断言操作:{action_detail},用例数据:{details},获取到的:{actual_value_str}")
            shot_png(driver, action_detail)
            sys.exit(1)
        else:
            loger.log("断言操作-{}:{}".format(action_detail, details))


def execute_swipe(driver, details, action_detail=None):
    element = details.get('locator')
    direction = details.get('direction')
    size = details.get('size')
    sleep = details.get('sleep')
    times = details.get('times')
    type = details.get('type')
    wait_until_element_disappears(driver)
    swipe_result= swipe_screen(driver, direction, size, sleep, times, element, type)
    if swipe_result is False:
        loger.error("滑动操作-{}:{}".format(action_detail, details))
        shot_png(driver, action_detail)
        sys.exit(1)
    else:
        loger.log("滑动操作-{}:{}".format(action_detail, details))


def execute_coordinate_click(driver, details, action_detail=None):
    template_path = details.get('template_path')
    sleep = details.get('sleep')
    instance = details.get('instance')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    coord = coordinate(driver, template_path, instance)
    if coord is not False and coord is not None:
        coord_click(coord, driver, sleep)
        loger.log("图片识别点击操作-坐标{}-{}:{}".format(coord, action_detail, details))
    else:
        loger.error("图片识别点击操作-坐标{}-{}:{}".format(coord, action_detail, details))
        shot_png(driver, action_detail)
        sys.exit(1)
def execute_sleep(driver, details, action_detail=None):
    sleep = details.get('sleep')
    time.sleep(sleep)
    loger.log("等待时间-{}-{}".format(details, action_detail))

def execute_return_to_homepage(driver, details, action_detail=None):
    sleep = details.get('sleep')
    text = return_to_homepage_and_get_last_text(driver, sleep)
    loger.log("返回首页-页面为{}".format(text))

def execute_press_key(driver, details, action_detail=None):
    key_name = details.get('locator')
    sleep = details.get('sleep')
    press_result = press_key(driver, key_name, sleep)
    if press_result:
        loger.log(f"按键操作{details}-{action_detail}")
    else:
        loger.error(f"按键操作{details}-{action_detail}")
        shot_png(driver, action_detail)
        sys.exit(1)
def execute_element_to_element(driver, details, action_detail=None):
    sleep = details.get('sleep')
    locator_text = details.get('locator')
    start_text = locator_text['start_text']
    end_text = locator_text['end_text']
    duration = details.get('duration')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    element_result = drag_element_to_element(driver, start_text, end_text, duration, sleep)
    if element_result:
        loger.log(f"属性滑动{details}-{action_detail}")
    else:
        loger.error(f"属性滑动{details}-{action_detail}")
        shot_png(driver, action_detail)
        sys.exit(1)
def execute_mock_payment(driver, details, action_detail=None):
    sleep = details.get('sleep')
    instance = details.get('instance')
    value = details.get('value')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    payment_result = mock_element_payment(driver, sleep, instance, value)
    if payment_result:
        loger.log(f"mock支付成功{details}-{action_detail}")
    else:
        loger.error(f"mock支付失败{details}-{action_detail}")
        sys.exit(1)

def execute_element_sibling(driver, details, action_detail=None):
    element = details.get('locator')
    instance = details.get('instance')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    order_result = payment_element_order(driver, element, instance)
    if order_result:
        loger.log(f"同级元素获取{details}-{action_detail}")
    else:
        loger.error(f"同级元素获取{details}-{action_detail}")
        sys.exit(1)

def execute_tap_numbers(driver, details, action_detail=None):
    value = details.get('value')
    numbers_resylt = tap_numbers(driver, value)
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    if numbers_resylt:
        loger.log(f"数字键盘输入{details}-{action_detail}")
    else:
        loger.error(f"数字键盘输入{details}-{action_detail}")
        shot_png(driver, action_detail)
        sys.exit(1)
def execute_swipe_left(driver, details, action_detail=None):
    element = details.get('locator')
    type = details.get('type')
    size = details.get('size')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    swipe_result = swipe_left_on_element(driver, type, element, size)
    if swipe_result:
        loger.log(f"滑动删除{details}-{action_detail}")
    else:
        loger.error(f"滑动删除{details}-{action_detail}")
        shot_png(driver, action_detail)
        sys.exit(1)

def execute_sending_df(driver, details, action_detail=None):
    value = details.get('value')
    number = details.get('number')
    coupon_type = details.get('coupon_type')
    send_result = pay_sending_df(value, number, coupon_type)
    if send_result is True:
        loger.log(f"派发{coupon_type}券{details}-{action_detail}")
    else:
        loger.error(f"派发{coupon_type}券{details}-接口错误{send_result['message']}-{action_detail}")
        sys.exit(1)
def execute_sql(driver, details, action_detail=None):
    query = details.get('sql_query')
    db_name = details.get('db_name')
    sql_result = connertion_sql(db_name, query)
    if sql_result:
        loger.log(f"SQL执行{details}-{action_detail}")
    else:
        loger.error(f"SQL执行{details}-{action_detail}")
        sys.exit(1)

def execute_points(driver, details, action_detail=None):
    value = details.get('value')
    points_result = add_points(value)
    if points_result:
        loger.log(f"长客会积分派发{details}-{action_detail}")
    else:
        loger.error(f"长客会积分派发{details}-{action_detail}")
        sys.exit(1)
def execute_search(driver, details, action_detail=None):
    sleep = details.get('sleep')
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    search_result = send_search(driver, sleep)
    if search_result:
        loger.log(f"键盘搜索{details}-{action_detail}")
    else:
        loger.error(f"键盘搜索{details}-{action_detail}")
        sys.exit(1)
def execute_async_task(driver, details, action_detail=None):
    sleep = details.get('sleep')
    async_xpath = details.get("async_xpath")
    click_steps = details.get("click_steps", [])
    wait_until_element_disappears(driver)
    dump_hierarchy(driver)
    actual_value = async_task(driver, async_xpath, click_steps, sleep)
    if isinstance(actual_value, (str, bool, int)):
        actual_value_str = str(actual_value).strip().replace("：", ":")
    else:
        loger.error(f"获取到的actual_value类型不受支持: {type(actual_value)}")
        actual_value_str = ""
    expected_value_str = str(details.get('value')).replace("：", ":")

    if actual_value_str != expected_value_str:
        loger.error(f"异步断言失败:{action_detail},用例数据:{details},获取到的:{actual_value_str}")
        shot_png(driver, action_detail)
        sys.exit(1)
    else:
        loger.log("异步断言成功-{}:{}".format(action_detail, details))


# 关键字到函数的映射
keyword_mapping = {
    "打开微信": execute_open_weixin,
    "点击": execute_click,
    "输入": execute_input,
    "断言": execute_assertion,
    "滑动": execute_swipe,
    "图片识别点击": execute_coordinate_click,
    "等待": execute_sleep,
    "返回首页": execute_return_to_homepage,
    "按键": execute_press_key,
    "属性滑动": execute_element_to_element,
    "支付mock": execute_mock_payment,
    "同级元素获取":  execute_element_sibling,
    "数字键盘输入": execute_tap_numbers,
    "滑动删除": execute_swipe_left,
    "派发电子券": execute_sending_df,
    "SQL执行": execute_sql,
    "长客会积分派送": execute_points,
    "键盘搜索": execute_search,
    "异步断言": execute_async_task
}


def get_index_from_string(s):
    """从字符串中提取索引。例如，从'index[0]'中提取0。如果没有找到索引，则返回None。"""
    match = re.search(r'index\[(\d+)\]', s)
    return int(match.group(1)) if match else None
def get_value_from_csv(csv_path, field_name, index=0):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if idx == index:
                return row[field_name]
    return None


def process_csv_in_details(details):
    try:
        for key in ['locator', 'value']:
            if key in details and '|' in details[key]:
                parts = details[key].split('|')
                csv_path = parts[0]
                field_name = parts[1]

                # 如果提供了index，则获取它，否则使用默认值0
                idx = get_index_from_string(parts[2]) if len(parts) > 2 else 0
                value_from_csv = get_value_from_csv(csv_path, field_name, idx)

                if value_from_csv:
                    details[key] = value_from_csv
    except Exception as e:
        loger.error(e)
def remove_newAccount(s):
    """从字符串中去除newAccount并仅返回括号中的数字。"""
    match = re.search(r'newAccount\((\d+)\)', s)
    return match.group(1) if match else s




def execute_actions(driver, data):
    for key, value in data.items():
        split_key = key.split('-')
        keyword = split_key[0]

        # 保存"-"后面的内容
        action_detail = split_key[1] if len(split_key) > 1 else None

        if keyword in keyword_mapping:
            try:
                keyword_mapping[keyword](driver, value, action_detail)
            except AssertionError as e:
                loger.error(e)
            except Exception as e:
                error_msg = f"执行关键字'{key}': {e}"
                loger.error(error_msg)

        if isinstance(value, dict):
            execute_actions(driver, value)
        elif key == "step" and isinstance(value, list):
            for step_data in value:
                execute_actions(driver, step_data)




def perform_actions(driver, test_data):
    for step_data in test_data:
        for key, value in step_data.items():
            if isinstance(value, dict):  # 传递它到execute_actions
                execute_actions(driver, value)
    if loger.has_errors():
        #loger.display_errors()
        raise Exception("报错信息：{}".format(loger.errors))
