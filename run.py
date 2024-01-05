# -*- coding: utf-8 -*-
from urllib.parse import quote
from common.config.metershpere import meter_run
import pytest
from common.base.case_executor import process_test_case, perform_actions
from common.config.path_utils import *
from common.base.device_initialization import start_weixin,get_device_ids,start_app
from common.config.loger import loger
import uiautomator2 as u2
import uiautomator2.ext.htmlreport as htmlreport
from common.config.case_initialization import case_shop_cart
from common.base.login_out_init import login_out_faile

@pytest.fixture(scope="session")
def driver_setup(request):
    driver = u2.connect(get_device_ids()[0])
    hrp = htmlreport.HTMLReport(driver, 'report')
    hrp.patch_click()
    yield driver




@pytest.fixture(autouse=True)
def clear_logger_before_test(request):
    loger.clear()
    delete_images()
    yield
    em = loger.has_errors()
    if em:
        driver = u2.connect(get_device_ids()[0])

        login_out_faile(driver)
@pytest.mark.parametrize('path', TESTCASE_PATHS)
def test_execute_actions(driver_setup, path):

    test_data = process_test_case(path)
    perform_actions(driver_setup, test_data)

def main():
    # 参数列表
    if start_package == 'app':
        delete_images()
        start_app()
        args = [
            '-vs',
            '--disable-warnings',
            'run.py',
            '--html=./reports/{}/{}.html'.format(current_dates, 'app测试报告'),
            '--self-contained-html',
        ]
    else:
        meter_run()
        #delete_images()
        start_weixin()
        args = [
            '-vs',
            '--disable-warnings',
            'run.py',
            '--html=./reports/{}/{}.html'.format(current_dates, '小程序报告'),
            '--self-contained-html',
            '--reruns', '1',  # 设置重试的次数，可以根据需求调整
            '--reruns-delay', '3',  # 重试之间的延迟，以秒为单位
        ]

    # 调用pytest.main传入参数
    pytest.main(args)

if __name__ == '__main__':
    main()