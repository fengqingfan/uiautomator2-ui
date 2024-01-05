import os
from datetime import datetime,timedelta
import configparser
import re,glob
import shutil

#项目路径，供全局调用
current_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_path)
parent_of_parent_directory = os.path.dirname(parent_directory)
#项目目录
grandparent_directory = os.path.dirname(parent_of_parent_directory)

config_file_path = '{}/common/config/config.ini'.format(grandparent_directory)
config = configparser.ConfigParser()
#报告图片参数配置
config.read(config_file_path, encoding='utf-8')
screenshot_count = int(config['SCREENSHOTS']['count'])
#报告目录日期
current_dates = datetime.today().strftime("%Y-%m-%d-%H_%M_%S")
#APP安装包目录
app_path = grandparent_directory + '/data/app_apk/'
# #启动配置
serial_number = config['startup_config']['serial_number']

start_wechat = config['startup_config']['start_wechat_package']
start_anliapp = config['startup_config']['start_app_package']

#启动测试应用选择
start_package = config['test_package']['start_package']


def get_all_testcase_paths(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files
#测试用例目录

test_path = config['test_case']['path']
TESTCASE_PATHS = get_all_testcase_paths(grandparent_directory+test_path)



#图片地址

def extract_names_from_matches(matched_strings):
    results = []
    pattern = r'\\([^\\]+)\.json'
    for matched_string in matched_strings:
        result = re.search(pattern, matched_string)
        if result:
            results.append(result.group(1))
    return results


def create_folder_by_date(directory, filename):
    #current_date = datetime.now().strftime('%Y-%m-%d')
    date_folder_path = os.path.join(directory, current_dates)
    # 先确保日期文件夹存在
    if not os.path.exists(date_folder_path):
        os.makedirs(date_folder_path)

    created_folders = []

    for value in filename:
        # 在日期文件夹下创建子文件夹
        sub_folder_path = os.path.join(date_folder_path, value)
        if not os.path.exists(sub_folder_path):
            os.makedirs(sub_folder_path)
        created_folders.append(sub_folder_path)

    return created_folders

#报告图片路径，截图路径以及报告目录获取

filenames = extract_names_from_matches(TESTCASE_PATHS)
new_folder = create_folder_by_date(grandparent_directory+"/reports", filenames)
#print(f"New folder created at: {new_folder}")


# 处理Unicode转义序列
def phico_path(path_string):
    #decoded_path = bytes(path_string, "utf-8").decode("unicode_escape")
    # 移除方括号
    clean_path = path_string.strip("[]")
    filename = os.path.basename(clean_path)
    name_without_extension = os.path.splitext(filename)[0]
    return name_without_extension

#用例名字获取
def name_code(test_name):
    #decoded_test_name = bytes(test_name, "utf-8").decode("unicode_escape")

    # 使用正则表达式提取文件名
    match = re.search(r'\\([^\\]+)\.json', test_name)
    if match:
        file_name = match.group(1)
        return file_name
    else:
        print("No match found!")

#目录下图片获取
def get_all_images_in_directory(directory):
    """获取目录下的所有图片文件"""
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    all_files = os.listdir(directory)
    return [os.path.join(directory, file) for file in all_files if
            any(file.endswith(ext) for ext in image_extensions) and file.startswith('img-')]


def get_latest_images(directory_path, count):
    """获取目录下最新的图片文件"""
    #screenshot_count = int(config['SCREENSHOTS']['count'])
    all_images = get_all_images_in_directory(directory_path)

    # 根据时间戳排序
    sorted_images = sorted(all_images, key=lambda x: int(os.path.basename(x).split('-')[1].split('.')[0]))
    for img in sorted_images[:-count]:
        os.remove(img)
    return sorted_images[-count:]


def clear_directory():
    """删除目录中的所有文件和子目录"""
    #current_date = datetime.today().data()
    dir_path = grandparent_directory + '/reports/' + current_dates
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def move_files(name_path):
    """迁移文件列表到目标目录"""
    destination_directory = grandparent_directory + '/reports/' + current_dates + '/' + name_path
    directory_path = grandparent_directory + '/report/' + 'imgs/'
    false_path = grandparent_directory + '/report/' + 'failed/'
    #图片的数量
    screenshot_count = int(config['SCREENSHOTS']['count'])
    failedshot_count = int(config['SCREENSHOTS']['failed_count'])
    passshot = config['SCREENSHOTS']['pass_ture']
    # 确保目标目录存在
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    #执行成功图片
    if passshot == 'True':
        files = get_latest_images(directory_path, screenshot_count)
        for file in files:
            shutil.move(file, destination_directory)
    #失败图片
    false_files = get_latest_images(false_path, failedshot_count)
    for filer in false_files:
        shutil.move(filer, destination_directory)
    return destination_directory


def clear_directories_older_than():
    """
    清理早于给定天数的所有文件夹及其内容。

    :param directory: 要清理的目录路径
    :param days: 要保留的天数
    """

    directory = grandparent_directory + '/reports'
    days = config['clear_directories_day']['day']
    try:
        # 获取限制日期（今天减去指定天数）
        limit_date = datetime.now() - timedelta(int(days))
        # 遍历指定目录中的所有文件夹
        for foldername in os.listdir(directory):
            folder_path = os.path.join(directory, foldername)
            if os.path.isdir(folder_path):
                folder_date_str= foldername.split('_')[0]
                try:
                    folder_date = datetime.strptime(folder_date_str, '%Y-%m-%d-%H')
                    if folder_date.date() < limit_date.date():
                        shutil.rmtree(folder_path)
                        print(f"删除文件夹: {folder_path}")
                except ValueError:

                    continue
    except Exception as e:
        print(f"清理时出现错误: {e}")
def delete_all_images(folder_path):
    # 构建图片文件的搜索模式
    image_pattern = os.path.join(folder_path, '*.jpg')

    # 获取所有匹配的图片文件路径
    image_files = glob.glob(image_pattern)

    # 删除每个图片文件
    for image_file in image_files:
        try:
            os.remove(image_file)
            print(f"Deleted: {image_file}")
        except Exception as e:
            print(f"Error deleting {image_file}: {e}")

def delete_images():
    folder_path_failed = grandparent_directory + '/report/failed'
    folder_path_imgs = grandparent_directory + '/report/imgs'
    delete_all_images(folder_path_failed)
    delete_all_images(folder_path_imgs)