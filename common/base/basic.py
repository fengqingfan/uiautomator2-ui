from findit import FindIt
from PIL import Image
import io,os,threading,queue,re
import time, cv2
from common.config.loger import loger
import tempfile
import numpy as np
from common.config.path_utils import grandparent_directory
from datetime import datetime
from common.config.mockpall import mock_payment
from common.base.courtesy_card import sending_df,points_add
from common.config.connertion_sql import mysql_connertion
from concurrent.futures import ThreadPoolExecutor


#强制元素加载
def dump_hierarchy(driver):
    driver.dump_hierarchy()

# 启动应用
def start_weixin(driver=None, sleep=None):
    driver.app_start("com.tencent.mm")
    time.sleep(sleep or 0)
#输入文字
def send_key(driver, value=None, sleep=None):
    try:
        driver.set_fastinput_ime(True)
        driver.clear_text()
        driver.send_keys(value)

        time.sleep(sleep or 0)
        return True
    except Exception as e:
        #loger.error(f"输入文本 {value} 时出错: {str(e)}")
        loger.special(f"输入文本 {value} 时出错: {str(e)}")
        return False  # 返回失败
def send_search(driver, sleep=None):
    try:
        driver.send_action('search')
        time.sleep(sleep or 0)
        return True
    except Exception as e:
        #loger.error(f"输入文本 {value} 时出错: {str(e)}")
        loger.special(f"键盘搜索时出错: {str(e)}")
        return False
#坐标点击
def coord_click(coord, driver, sleep=None):
    x, y = coord
    driver.click(int(x), int(y))
    time.sleep(sleep or 2)
#元素定位点击
def element_click(driver=None, type=None, element=None, sleep=None, instance=None, timeout=5.0):
    if not element:
        loger.special(f"未提供元素定位信息: {element}")
        return False

    strategies = {
        "text": lambda: driver(text=element, instance=instance),
        "xpath": lambda: driver.xpath(element),
        "resourceId": lambda: driver(resourceId=element, instance=instance),
        "className": lambda: driver(className=element, instance=instance),
        "textMatches": lambda: driver(textMatches=element, instance=instance),
        "description": lambda: driver(description=element, instance=instance)
    }

    if type:
        strategies = {type: strategies[type]}

    last_exception = None
    for strategy_func in strategies.values():
        strategy = strategy_func()

        try:
            # 使用 wait 方法等待元素出现，超时时间为指定的 timeout
            strategy.wait(timeout=timeout)
            # 执行点击操作

            strategy.click()
            time.sleep(sleep or 0)
            return True
        except Exception as e:
            last_exception = e

    loger.special(f"未找到元素: {element} 尝试点击元素详细错误是: {last_exception}")
    return False

# def try_strategy(strategy, result_queue, found_event):
#     if found_event.is_set():
#         return
#     #strategy_start = time.time()
#     try:
#         if strategy.wait(4):
#             if not found_event.is_set():
#                 result_queue.put(strategy)
#                 found_event.set()
#     except Exception as e:
#         if not found_event.is_set():
#             result_queue.put(e)
    #finally:
        #strategy_duration = time.time() - strategy_start
        #loger.log(f"Strategy '{strategy}' took {strategy_duration:.2f} seconds.")

# #点击
# def element_click(driver=None, type=None, element=None, sleep=None, instance=None):
#     if not element:
#         loger.special(f"未提供元素定位信息: {element}")
#         return False
#     strategies = {
#         "text": lambda: driver(text=element, instance=instance),
#         "xpath": lambda: driver.xpath(element),
#         "resourceId": lambda: driver(resourceId=element, instance=instance),
#         "className": lambda: driver(className=element, instance=instance),
#         "textMatches": lambda: driver(textMatches=element, instance=instance)
#     }
#     if type:
#         strategies = {type: strategies[type]}
#     last_exception = None
#     result_queue = queue.Queue()
#     threads = []
#     #start_time = time.time()
#     found_event = threading.Event()
#     for strategy_func in strategies.values():
#         strategy = strategy_func()
#         t = threading.Thread(target=try_strategy, args=(strategy, result_queue, found_event))
#         t.start()
#         threads.append(t)
#
#     for t in threads:
#         t.join(timeout=5)  # 设置超时时间为5秒
#     # duration = time.time() - start_time  # 计算查找所消耗的时间
#     # loger.log(f"查找元素 '{element}' 耗时: {duration:.2f} 秒")
#     while not result_queue.empty():
#         result = result_queue.get()
#         if isinstance(result, Exception):
#             last_exception = result
#             continue
#         if result.exists:
#             try:
#                 result.click()
#                 time.sleep(sleep or 0)
#                 return True
#             except Exception as e:
#                 last_exception = e
#                 continue
#
#     loger.special(f"未找到元素: {element}  尝试点击元素详细错误是: {last_exception}")
#     return False
def element_find(driver=None, type=None, element=None, sleep=None, instance=None, timeout=5.0):
    if not element:
        loger.special(f"未提供元素定位信息: {element}")
        return False

    strategies = {
        "text": lambda: driver(text=element, instance=instance),
        "xpath": lambda: driver.xpath(element),
        "resourceId": lambda: driver(resourceId=element, instance=instance),
        "className": lambda: driver(className=element, instance=instance),
        "textMatches": lambda: driver(textMatches=element, instance=instance),
        "textContains": lambda: driver(textContains=element, instance=instance)
    }
    if type:
        strategies = {type: strategies[type]}

    last_exception = None

    for strategy_func in strategies.values():
        strategy = strategy_func()
        try:
            # 使用 wait 方法等待元素出现，超时时间为指定的 timeout
            strategy.wait(timeout=timeout)
            # 获取元素的文本值
            text_value = strategy.get_text()
            if text_value:
                time.sleep(sleep or 0)
                return text_value
            else:
                return True
        except Exception as e:
            last_exception = e

    loger.special(f"未找到元素: {element} 尝试查找元素详细错误是: {last_exception}")
    return False
#
# #断言或元素查找
# def element_find(driver, type=None, element=None, sleep=None, instance=None):
#     if not element:
#         loger.special(f"未提供元素定位信息: {element}")
#         return False
#     strategies = {
#         "text": lambda: driver(text=element, instance=instance),
#         "xpath": lambda: driver.xpath(element),
#         "resourceId": lambda: driver(resourceId=element, instance=instance),
#         "className": lambda: driver(className=element, instance=instance),
#         "textMatches": lambda: driver(textMatches=element, instance=instance),
#         "textContains": lambda: driver(textContains=element, instance=instance)
#     }
#     if type:
#         strategies = {type: strategies[type]}
#     last_exception = None
#     found_queue = queue.Queue()
#     #start_time = time.time()
#     threads = []
#     found_event = threading.Event()
#     for strategy_func in strategies.values():
#         strategy = strategy_func()
#         t = threading.Thread(target=try_strategy, args=(strategy, found_queue, found_event))
#         t.start()
#         threads.append(t)
#
#     for t in threads:
#         t.join(timeout=5)  # 设置超时时间为5秒
#     #duration = time.time() - start_time
#     #loger.log(f"查找元素 '{element}' 耗时: {duration:.2f} 秒")
#     while not found_queue.empty():
#         result = found_queue.get()
#
#         if isinstance(result, Exception):
#             last_exception = result
#             continue
#
#         if result and result.exists:
#             # if type == "textMatches":
#             #     return result.info.get('text', '')
#             text_value = result.get_text()
#             if text_value:
#                 return text_value
#             time.sleep(sleep or 0)
#             return True
#
#     loger.special(f"未找到元素: {element}  尝试查找元素详细错误是: {last_exception}")
#     return False


#截图,可提供保存地址，可提供坐标区域截图
def screenshot(pic_path=None, driver=None, coord=None):
    raw_image = driver.screenshot(format='raw')
    # 将 bytes 类型的截图转换为 PIL.Image 类型
    image = Image.open(io.BytesIO(raw_image))
    if coord:
        try:
            image = image.crop(coord)
        except:
            raise ValueError("提供正确的坐标")
    if pic_path:
        image.save(pic_path)
    else:
        return image


#获取元素信息
def element_info(driver=None, element=None):
    #获取到所有坐标
    element = driver.xpath(element).info
    return element
#根据元素位置坐标获取
def coordinate_xpath(driver=None,element=None):
    element = element_info(driver, element)['bounds']
    # 获取坐标中间值
    elementx = (element['right'] - element['left']) / 2 + element['left']
    elementy = (element['bottom'] - element['top']) / 2 + element['top']
    return elementx, elementy


#根据图片对象获取坐标定位
def find_key_in_dict(d, target_key):
    if target_key in d:
        return d[target_key]
    for key, value in d.items():
        if isinstance(value, dict):
            result = find_key_in_dict(value, target_key)
            if result is not None:
                return result
    return None


def merge_nearby_coords(coords, distance_threshold=5, return_index=None):
    merged_coords = []
    #print(coords)
    for coord in coords:
        if not any([np.linalg.norm(np.array(coord) - np.array(mc)) < distance_threshold for mc in merged_coords]):
            merged_coords.append(coord)

    if return_index is not None and 0 <= return_index < len(merged_coords):
        return [merged_coords[return_index]]
    return merged_coords

def coordinate(driver, template_path=None, instance=None):
    if not template_path:
        loger.error("未提供目标路径或模板路径。")
        return None

    time.sleep(2)
    screenshot_image = driver.screenshot(format='pillow')

    # 读取中文路径的图片
    chinese_image_path = grandparent_directory + '/data/template_path/' + template_path
    target_image = Image.open(chinese_image_path)

    fd_target, temp_target_path = tempfile.mkstemp(suffix=".png")
    os.close(fd_target)
    target_image.save(temp_target_path)
    fd, temp_path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    screenshot_image.save(temp_path)
    if instance is None:
        instance = 0
    try:
        screen_img = cv2.imread(temp_path, cv2.IMREAD_GRAYSCALE)
        target_img = cv2.imread(temp_target_path, cv2.IMREAD_GRAYSCALE)
        h, w = target_img.shape[:2]
        match_matrix = cv2.matchTemplate(screen_img, target_img, cv2.TM_CCOEFF_NORMED)
        loc = np.where(match_matrix >= 0.90)
        all_matches = [(x + w // 2, y + h // 2) for x, y in zip(*loc[::-1])]
        os.remove(temp_path)
        os.remove(temp_target_path)
        merged_coords = merge_nearby_coords(all_matches, return_index=instance)
        if merged_coords and merged_coords is not None:
            return merged_coords[0]  # 返回一个坐标
        else:
            return None
    except Exception as e:
        loger.error(f"获取图片坐标发生错误: {str(e)}")
        return False





def swipe_screen(driver=None, direction=None, size=None, sleep=None, times=None, element=None, type=None):
    if not driver or not direction:
        loger.error("Driver或滑动方向未提供。")
        return False

    width, height = driver.window_size()
    y = int(height/2)
    x = int(width/2)
    if element and type:
        if type == 'text':
            ui_element = driver(text=element)
        elif type == 'resourceId':
            ui_element = driver(resourceId=element)
        elif type == 'xpath':
            ui_element = driver.xpath(element)
        if ui_element and ui_element.exists:
            element_bounds = ui_element.center()
            x, y = element_bounds
        else:
            loger.error(f"未找到元素: {element} 使用 {type} 方法。")
    if size is not None and size == 0:
        return True
    if times is None:
        times = 1
    for _ in range(times):
        try:
            if direction == 'up':
                """向上滑动"""
                swipe_y = y - size if size else y - int(height / 3)
                driver.swipe(x, y, x, swipe_y)
            elif direction == 'down':
                """向下滑动"""
                swipe_y = y + size if size else y + int(height / 3)
                driver.swipe(x, y, x, swipe_y)
            elif direction == 'left':
                """向左滑动"""
                swipe_x = x - size if size else x - int(width / 3)
                driver.swipe(x, y, swipe_x, y)
            elif direction == 'right':
                """向右滑动"""
                swipe_x = x + size if size else x + int(width / 3)
                driver.swipe(x, y, swipe_x, y)
            else:
                loger.error('提供的滑动方向无效。')
                return False
            time.sleep(2)
        except Exception as e:
            loger.error(f"执行滑动操作时出错：{str(e)}")
            return False
    time.sleep(sleep)
    return True

#截图
def shot_png(driver, name):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    screenshot_name = f"report/failed/img-{timestamp}-{loger.step_counter}-{name}.jpg"
    driver.screenshot(screenshot_name)

#判断页面并返回第一级页面
def return_to_homepage_and_get_last_text(driver, sleep):
    """返回到首页，并根据当前页面返回对应的文本"""
    try:
        resource_id = "com.tencent.mm:id/hc"
        count_list = [
            '云逛街',
            '产品分类',
            '购物车',
            '我的'
        ]
        # 获取与指定resourceId匹配的元素数量
        count = driver(resourceId=resource_id).count
        # 根据count的值，决定如何处理文本
        if count == 0:
            return "首页"
        else:
            for instance in range(count):
                text = driver(resourceId=resource_id, instance=instance).get_text()
                text_index = driver(resourceId=resource_id, instance=0).get_text()
                if text in count_list:
                    for _ in range(count - 1):  # 按返回键 count - instance 次
                        driver.press("back")
                        time.sleep(1)
                    time.sleep(sleep)
                    return text_index
            text_index = driver(resourceId=resource_id, instance=0).get_text()
            for _ in range(count):  # 按返回键 count-1 次
                driver.press("back")
                time.sleep(1)
            time.sleep(sleep)
            return text_index

    except Exception as e:
        loger.special(f"返回页面 时出错: {str(e)}")

#判断加载元素是否消失
def wait_until_element_disappears(driver):
    """等待元素消失直到达到最大等待时间"""
    return driver(resourceId="com.tencent.mm:id/mvs").wait_gone(timeout=20)

#按键操作
def press_key(driver, key_name, sleep=None):
    try:
        driver.press(key_name)
        time.sleep(sleep or 0)
        return True
    except Exception as e:

        loger.special(f"返回页面 时出错: {str(e)}")
        return False

#滑动属性
def drag_element_to_element(driver, start_text, end_text, duration=None, sleep=None):
    try:
        driver(text=start_text).drag_to(text=end_text, duration=duration or 0.5)
        time.sleep(sleep or 0)
        return True
    except Exception as e:
        loger.special(f"元素属性滑动出错: {str(e)}")
        return False
#mock支付提供元素
def mock_element_payment(driver, sleep, instance=None, value=None):
    try:
        order_number = payment_element_order(driver, '订单编号：', instance)
        if value is None:
            buyer_text = payment_element_order(driver, '购货人：', instance)
            result_ada = re.search(r'\((\d+)\)', buyer_text)
            if result_ada:
                value = result_ada.group(1)
        total_amount = payment_element_order(driver, '订单总额：', instance)
        payment_amount_result = re.search(r'[\d.]+', total_amount)
        if payment_amount_result:
            payment_amount = payment_amount_result.group()
        result_status = mock_payment(order_number, value, payment_amount)
        time.sleep(sleep or 0)
        return result_status
    except Exception as e:
        loger.special(f"mock支付出错: {str(e)}")
        return False
#页面元素提供,查找相邻元素
def payment_element_order(driver, element=None, instance=None, timeout=5.0):
    try:
        order_label = driver(text=element)
        order_label.wait(timeout=timeout)
        # 如果找到了这个TextView
        if order_label.exists:
            # 在父容器中获取所有的TextView元素
            all_textviews_in_container = order_label.sibling(className="android.widget.TextView")
            target_position = None
            # 遍历容器中的所有TextView元素，找到目标文本的位置
            for i in range(all_textviews_in_container.count):
                if all_textviews_in_container[i].get_text() == element:
                    target_position = i
                    break
            target_text = driver(text=element).sibling(className="android.widget.TextView", instance=target_position + instance).get_text()
            return target_text
    except Exception as e:
        loger.special(f"相邻元素查找出错: {str(e)}")
        return False

#数字键盘
def tap_numbers(driver, value):
    try:
        # 建立数字与resourceId的映射
        mapping = {
            '0': "tenpay_keyboard_0",
            '1': "tenpay_keyboard_1",
            '2': "tenpay_keyboard_2",
            '3': "tenpay_keyboard_3",
            '4': "tenpay_keyboard_4",
            '5': "tenpay_keyboard_5",
            '6': "tenpay_keyboard_6",
            '7': "tenpay_keyboard_7",
            '8': "tenpay_keyboard_8",
            '9': "tenpay_keyboard_9"
        }
        driver(resourceId="com.tencent.mm:id/tenpay_keyboard_d").click(timeout=3)
        if isinstance(value, int):
            numbers = str(value)
        for num in value:
            if num not in mapping:
                raise ValueError(f"无效的数字：{num}")

            # 获取resourceId并点击相应的数字
            resource_id = f"com.tencent.mm:id/{mapping[num]}"
            driver(resourceId=resource_id).click()
        driver.xpath('//*[@resource-id="com.tencent.mm:id/b3f"]/android.widget.ImageView[1]').click()
        return True
    except Exception as e:
        loger.special(f"数字键盘点击出错: {str(e)}")
        return False


#滑动删除
def swipe_left_on_element(driver, type, element, size=None):
    try:
        # 使用动态属性选择器定位元素
        if type == "text":
            elements = driver(text=element)
        else:
            elements = driver.xpath(element).get()
        # 确保元素存在
        if elements.exists:
            center_x, center_y = elements.center()
            if size is None:
                size = 100
            end_x = center_x - int(size)
            end_y = center_y
            # 执行滑动操作
            driver.swipe(center_x, center_y, end_x, end_y)
            return True
    except Exception as e:
        loger.special(f"滑动删除找出错: {str(e)}")
        return False
#DF券发送
def pay_sending_df(value, number, coupon_type):
    try:
        status_code = sending_df(value, number, coupon_type)
        if status_code['code'] == "0":
            return True
        else:
            return status_code
    except Exception as e:
        loger.special(f"DF券发送出错: {str(e)}")
        return False

#长客会积分派发
def add_points(value):
    try:
        status_code = points_add(value)
        if status_code:
            return True
        else:
            return status_code
    except Exception as e:
        loger.special(f"长客会积分发送出错: {str(e)}")
        return False



#sql语句执行
def connertion_sql(db_name, query):
    try:
        status_code = mysql_connertion(db_name, query)
        if status_code:
            return True
    except Exception as e:
        loger.special(f"SQL语句执行出错: {str(e)}")
        return False

#异步处理断言
def async_operation(d, async_xpath):
    try:
        actual_data = d.xpath(async_xpath).get_text()
        return actual_data
    except Exception as e:
        loger.special(f"异步处理出错: {str(e)}")
        return None

def async_task(d, async_xpath, click_steps, sleep):
    try:
        # 开启异步操作
        with ThreadPoolExecutor() as executor:
            # 提交异步任务到线程池
            future = executor.submit(async_operation, d, async_xpath)
        # 进行主步骤执行
            for step_xpath in click_steps:
                d.xpath(step_xpath).click()
                time.sleep(sleep or 1)
        result = future.result()
        # 处理异步任务的结果
        if result is not None:
            return result
        else:
            return False
    except Exception as e:
        loger.special(f"异步处理出错: {str(e)}")
