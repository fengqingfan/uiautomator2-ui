
from common.base.basic import element_click, swipe_screen, return_to_homepage_and_get_last_text, \
    wait_until_element_disappears, coordinate, coord_click




def login_out_faile(driver):
    return_to_homepage_and_get_last_text(driver, 2)
    wait_until_element_disappears(driver)
    element_click(driver, 'text', '我的', 2)
    wait_until_element_disappears(driver)
    swipe_screen(driver, 'up', 500, 2, 6)
    element_click(driver, 'text', '解绑微信并退出', 2)
    wait_until_element_disappears(driver)
    element_click(driver, 'text', '确定', 3)
    wait_until_element_disappears(driver)
    element_click(driver, 'xpath', '//*[@resource-id="app"]/android.view.View[2]', 3)
    wait_until_element_disappears(driver)
    coord = coordinate(driver, '退出登陆/login-out1.png')
    coord_click(coord, driver)
    wait_until_element_disappears(driver)
    coord1 = coordinate(driver, '退出陆/login-out2.png')
    coord_click(coord1, driver)
    wait_until_element_disappears(driver)
    element_click(driver, 'text', '我知道了', 2)
