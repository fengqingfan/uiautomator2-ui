import uiautomator2 as u2

from common.config.loger import loger
import subprocess
from common.config.path_utils import start_wechat,clear_directory,clear_directories_older_than,start_anliapp,app_path
import time,os


def initialize_uiautomator2():
    """
    执行UI2初始化命令
    """
    try:
        result = subprocess.check_output(["python", "-m", "uiautomator2", "init"], stderr=subprocess.STDOUT)
        print(result.decode("utf-8"))
        return True
    except subprocess.CalledProcessError as e:
        print("执行初始化命令时出错:", e.output.decode("utf-8"))
        return False

def uninstall_atx_package():

    command = ["adb"]
    device_id = get_device_ids()[0]
    if device_id:
        command.extend(["-s", device_id])
    command.extend(["uninstall", "com.github.uiautomator"])
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        print(result.decode("utf-8"))
        return "Success" in result.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print("尝试卸载包时出错:", e.output.decode("utf-8"))
        return False

def get_device_ids():
    try:
        # 执行adb devices命令并获取输出
        result = subprocess.check_output(["adb", "devices"], stderr=subprocess.STDOUT)
        result_str = result.decode("utf-8")

        # 解析输出以获取设备ID
        lines = result_str.strip().split("\n")[1:]
        device_ids = [line.split("\t")[0] for line in lines if "\tdevice" in line]
        return device_ids

    except Exception as e:
        print(f"获取设备ID时出错: {str(e)}")
        return []
def find_apks_in_directory():
    """获取目录下的所有APK文件"""
    return [os.path.join(app_path, f) for f in os.listdir(app_path) if f.endswith('.apk')]

def install_apk(apk_path):
    """使用ADB安装APK"""
    cmd = ["adb", "install", "-r", apk_path]
    subprocess.run(cmd)


def watchers_start(driver):
    # watchers_dict = {
    #     "安装": {"when_text": "USB安装提示", "click_text": "继续安装"}
    # }
    # for watcher_name, rules in watchers_dict.items():
    driver.watcher('watcher_name').when('USB安装提示').when("继续安装").click()
    driver.watcher('watcher_name').when('是否允许“安利”发送通知').when("始终允许").click()
    driver.watcher('watcher_name').when('用户个人信息保护说明').when("同意并继续").click()
    driver.watcher.start()
def init_device():
    """
    初始化设备并返回driver对象。
    """
    clear_directories_older_than()
    clear_directory()
    #initialize_uiautomator2()
    d = u2.connect(get_device_ids()[0])
    device_info = d.device_info
    #d.app_start("com.github.uiautomator")
    #d(text="启动UIAUTOMATOR").click()
    d.uiautomator.start()
    #d.implicitly_wait(10.0)
    loger.set_device_description(device_info)
    return d
def start_weixin():
    driver = init_device()

    time.sleep(3)

def start_app():
    driver = init_device()
    watchers_start(driver)
    apk_file = find_apks_in_directory()
    install_apk(apk_file[0])
    driver.app_start(start_anliapp)
