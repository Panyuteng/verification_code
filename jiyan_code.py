
import requests
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
from PIL import Image
from io import BytesIO


BORDER = 6
INIT_LEFT = 60


class JiyanCode():
    def __init__(self):
        self.url = 'http://account.geetest.com/login'
        self.bro = webdriver.Chrome()
        self.wait = WebDriverWait(self.bro, 20)
        self.email = '815490913@qq.com'
        self.password = '123456'

    def __del__(self):
        self.bro.close()

    def get_url(self):
        """
        打开url，填写密码
        :return:
        """
        self.bro.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def get_button(self):
        """
        模拟点击初始验证
        :return:
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        button.click()

    def get_position(self):
        """
        获取验证码位置
        :return:验证码位置元组
        """
        # image = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img geetest_absolute')))
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screen(self):
        """
        获取页面截图
        :return:
        """
        screen = self.bro.get_screenshot_as_png()
        screen = Image.open(BytesIO(screen))
        return screen

    def get_image(self):
        """
        获取验证码图片
        :return:
        """
        top, bottom, left, right = self.get_position()
        screen = self.get_screen()
        cap = screen.crop((left, top, right, bottom))
        return cap

    def get_slider(self):
        """
        获取滑块对象
        :return:
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1:不带缺口的图片（初始图片）
        :param image2:带缺口的图片（按了滑块的图片
        :param x:位置x
        :param y:位置y
        :return:像素是否相同
        """
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        num = 60
        if abs(pixel1[0] - pixel2[0]) < num and abs(pixel1[1] - pixel2[1]) < num and abs(
                pixel1[2] - pixel2[2]) < num:
            return 1
        else:
            return 0

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1:不带缺口的图片（初始图片）
        :param image2:带缺口的图片（按了滑块的图片）
        :return:缺口偏移量
        """
        left = 60
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance:偏移量
        :return:移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider:滑块
        :param track:轨迹
        :return:
        """
        ActionChains(self.bro).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.bro).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.bro).release().perform()

    def login(self):
        """
        登录
        :return:
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login-btn')))
        submit.click()
        time.sleep(3)
        print('登录成功')

    def crack(self):
        """
        登录的接口
        :return:
        """
        self.get_url()  # 打开webdriver，输入用户密码
        self.get_button()
        image1 = self.get_image()
        slider = self.get_slider()
        slider.click()
        image2 = self.get_image()
        gap = self.get_gap(image1, image2)
        gap -= BORDER
        track = self.get_track(gap)
        self.move_to_gap(slider, track)

        success = self.wait.until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
        return success

    def main(self):
        """
        程序入口
        :return:
        """
        success = self.crack()
        if success:
            self.login()
        else:
            for i in range(5):
                success = self.crack()
                if success:
                    break


if __name__ == '__main__':
    jiyan_code = JiyanCode()
    jisu_code.main()
