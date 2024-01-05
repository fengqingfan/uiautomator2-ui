import pytest
from py.xml import html
import configparser
import re,shutil,os,sys
from datetime import datetime
from common.config.path_utils import name_code,move_files,get_all_images_in_directory,delete_images,config
from common.config.loger import loger

def pytest_collection_modifyitems(items):
    """测试用例收集完成时，将收集到的item的name和nodeid的中文显示在控制台上:return:"""
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

def pytest_html_report_title(report):
    report.title = "小程序-云购微店测试-UI自动化报告"


def pytest_metadata(metadata):
    device_description = loger.get_device_description()
    #metadata["测试设备"] = "小米10"
    metadata["项目名称"] = "云购微店测试"  # 新增
    metadata["Brand"] = device_description['brand']
    metadata["model"] = device_description['model']
    metadata["version"] = device_description['version']
    metadata["display"] = device_description['display']
    metadata.pop("Packages")
    metadata.pop("Platform")
    metadata.pop("Plugins")
    metadata.pop("Python")


def pytest_runtest_setup(item):
    path = item.nodeid

    pattern = r"\[.*\]"

    match = re.search(pattern, path)
    if match:
        item.user_properties.append(("path", match.group()))

        return match.group()
    return None


def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([html.p("小程序自动化")])
    prefix.extend([html.p("执行人员： cat菠萝头")])


def pytest_html_results_table_header(cells):
    cells.pop()
    cells.pop(1)
    #cells.insert(2, html.th("Time", class_="sortable time", col="time"))
    #cells.insert(3, html.th('Screenshot', class_='sortable'))
    cells.insert(1, html.th('path', class_='path'))








def pytest_html_results_table_row(report, cells):
    cells.pop()
    cells.pop(1)
    path = report.user_properties[0][1] if report.user_properties else ""
    cells.insert(1, html.td(path))

from pytest_html import extras
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    test_name = name_code(item.nodeid)
    filename_with_extension = os.path.basename(test_name)
    # 使用os.path.splitext分割文件名和扩展名，并只返回文件名部分
    filename_without_extension = os.path.splitext(filename_with_extension)[0]
    new_paths = move_files(filename_without_extension)
    new_image_paths = get_all_images_in_directory(new_paths)

    pytest_html = item.config.pluginmanager.getplugin("html")
    out_time = yield
    report = out_time.get_result()
    extra = getattr(report, "extra", [])
    if report.when == "call" and new_image_paths:
        for image_path in new_image_paths:
            image_filename = os.path.basename(image_path)
            relative_image_path = os.path.join(image_filename)
            image_data = pytest_html.extras.image(test_name + '/' + relative_image_path, mime_type="image/jpeg")
            image_data['name'] = image_filename
            #extra.append(pytest_html.extras.image(test_name + '/' + relative_image_path, mime_type="image/jpeg"), name=image_filename)
            extra.append(image_data)

    report.extra = extra



def pytest_html_results_table_html(report, data):
    del data[:]

    logs_html = "<div class='logs' style='max-width: 100%;'>"
    for log in loger.logs:
        logs_html += "<p style='max-width: 1200px; word-wrap: break-word; line-height: " \
                           "normal;margin-bottom: 5px;'>{}</p>".format(log)
    logs_html += "</div>"
    if report.passed:
        data.append(logs_html)

    if report.failed:
        data.append(logs_html)  # 添加logs内容

        errors_html = "<div class='errors' style='max-width: 100%;margin-right: 20px;'>"
        for error in loger.errors:
            errors_html += "<p style='color: red;height: 100px; max-height: 120px; max-width: 500px; word-wrap: break-word; line-height: " \
                           "normal;margin-bottom: 5px;'>{}</p>".format(error)
        errors_html += "</div>"

        specials_html = "<div class='specials' style='max-width: 100%;margin-right: 20px;'>"
        for special in enumerate(loger.special_logs, start=1):
            specials_html += "<p style='color: red;height: 100px; max-height: 120px;max-width: 500px; line-height: normal; word-wrap: " \
                             "break-word;margin-bottom: 5px;'>详细错误：{}</p>".format(special)
        specials_html += "</div>"

        combined_html = "<div style='display: flex; justify-content: flex-start; align-items: flex-start;'>"
        combined_html += errors_html + specials_html
        combined_html += "</div>"

        data.append(combined_html)
    if report.rerun:
        data.append(logs_html)  # 添加logs内容

        errors_html = "<div class='errors' style='max-width: 100%;margin-right: 20px;'>"
        for error in loger.errors:
            errors_html += "<p style='color: red;height: 100px; max-height: 120px; max-width: 500px; word-wrap: break-word; line-height: " \
                           "normal;margin-bottom: 5px;'>{}</p>".format(error)
        errors_html += "</div>"

        specials_html = "<div class='specials' style='max-width: 100%;margin-right: 20px;'>"
        for special in enumerate(loger.special_logs, start=1):
            specials_html += "<p style='color: red;height: 100px; max-height: 120px;max-width: 500px; line-height: normal; word-wrap: " \
                             "break-word;margin-bottom: 5px;'>详细错误：{}</p>".format(special)
        specials_html += "</div>"

        combined_html = "<div style='display: flex; justify-content: flex-start; align-items: flex-start;'>"
        combined_html += errors_html + specials_html
        combined_html += "</div>"

        data.append(combined_html)

# def pytest_sessionfinish(session, exitstatus):
#     """Called after whole test run finished, right before returning the exit status to the system."""
#     loger.clear()


# def pytest_exception_interact(node, call, report):
#     if report.failed:
#         print(f"Test case failed in rer Running cleanup code.")
#             # 添加你的清理操作

