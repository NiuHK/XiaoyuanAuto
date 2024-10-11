import cv2
import numpy as np
import matplotlib.pyplot as plt
import socket
import sys
import time
import struct
from collections import OrderedDict
import os
import threading
from PIL import Image
import subprocess
import math

from libs.cv_match import match_template
from libs.minicap import cv2_latest_image, ImageBuffer, Minicap, Banner
import libs.adb as adb

class Execution:

    def __init__(self,serialNumber=None):
        self.serialNumber = serialNumber
        
        self.adbkit = adb.adbKit(self.serialNumber)
        

        self.forward_minicap_port()
        
        self.w, self.h = self.get_screen_resolution()
        # 自动分辨率
        try:
            # 启动 minicap 进程
            if self.serialNumber is not None:
                self.process = subprocess.Popen(
                    ['adb', '-s', self.serialNumber, 'shell', 'LD_LIBRARY_PATH=/data/local/tmp', '/data/local/tmp/minicap', '-P', f'{self.w}x{self.h}@{self.w}x{self.h}/0'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                self.process = subprocess.Popen(
                    ['adb', 'shell', 'LD_LIBRARY_PATH=/data/local/tmp', '/data/local/tmp/minicap', '-P', f'{self.w}x{self.h}@{self.w}x{self.h}/0'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            # 等待一段时间以确保 minicap 正在运行
            time.sleep(1)
            mc = Minicap('localhost', 1717, Banner())
            mc.connect()
            buffer_size = 5  # 缓冲区大小
            self.image_buffer = ImageBuffer(buffer_size)

            # Create a thread for the consume method
            self.consume_thread = threading.Thread(target=mc.consume, args=(self.image_buffer,))
            self.consume_thread.daemon = True  # Set the thread as a daemon thread
            self.consume_thread.start()  # Start the thread
            time.sleep(1)
            print("""---------------------[Execution] service initialized----------------------
                  若仍然无minicap推流，尝试撤销usb调试授权重新打开""")
        except Exception as e:
            print(f"[Execution] Initialization failed: {e}")

    def get_screen_resolution(self):
        result=self.adbkit.command('shell wm size')[1]
        output = result
        # 解析输出
        resolution = output.split()[-1]
        w, h = resolution.split('x')
        print(f"[Execution] Screen resolution: {w}x{h}")
        return int(w), int(h)
    
    def forward_minicap_port(self):
        try:
            self.adbkit.command('forward --remove tcp:1717 localabstract:minicap')
            print("[Execution] Port forwarding successful.")
        except subprocess.CalledProcessError as e:
            print(f"[Execution] Failed to forward port: {e}")
            
            
    def __del__(self):
        self.cleanup()

    def cleanup(self):
        print("[execution] Exiting...")
        if hasattr(self, 'process'):
            self.process.terminate()  # 或者 process.kill()
            print("[execution] minicap终止")
        if hasattr(self, 'consume_thread') and self.consume_thread.is_alive():
            self.consume_thread.join(timeout=1)
            print("[execution] consume_thread终止")

    def run(self):
        return self.result

    def find_templete(self, find_img_path, value=0.8, print_info=False, img=None):
        """
        查找模板图像在目标图像中的位置。

        参数:
        find_img_path (str): 要查找的模板图像的路径。
        value (float, 可选): 匹配阈值，默认为 0.8。
        print_info (bool, 可选): 是否打印调试信息并显示图像，默认为 False。
        img (numpy.ndarray, 可选): 目标图像。如果为 None，则从图像缓冲区中获取最新图像。
        目的是直接就之前颜色匹配的图像进行识别,减少缓冲区读写,某些场景下可以提高识别速度

        返回:
        tuple: 包含最佳匹配的图像区域和匹配位置的元组。如果未找到匹配项，则返回 (None, None)。

        异常:
        如果读取图像失败或发生其他异常，打印错误信息。
        """
        try:
            if img is not None:
                target_img = img
            else:
                target_img = cv2_latest_image(self.image_buffer)
            find_img = cv2.imread(find_img_path)

            if target_img is None or find_img is None:
                print(f"[find_templete] Failed to read images: target_img:{target_img is not None} find_img:{find_img is not None}")
                return None, None

            best_match, best_val, best_loc = match_template(target_img, find_img)

            if print_info:
                # 使用最佳匹配绘制矩形框
                h, w = best_match.shape[:2]
                bottom_right = (best_loc[0] + w, best_loc[1] + h)
                middle_point = (best_loc[0] + w // 2, best_loc[1] + h // 2)
                # 保存图片
                save_path = 'latest_image.jpg'  # 指定保存路径
                cv2.imwrite(save_path, target_img)
                
                cv2.circle(target_img, middle_point, 5, (0, 0, 255), -1)
                cv2.rectangle(target_img, best_loc, bottom_right, (0, 255, 0), 2)

                target_img_rgb = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)
                plt.imshow(target_img_rgb)
                plt.axis('off')  # 隐藏坐标轴
                plt.show()
                
                print(f"[Execution.find_templete]  Best match value: {best_val}")
                print(f"[Execution.find_templete]  Best match location: {best_loc}")
                
                
            if best_val >= value:
                return best_match, best_loc
            else:
                print("[Execution.find_templete] not found")
        except Exception as e:
            print(f"[Execution.find_templete] Error: {e}")
        return None, None

    def wait_templete(self, find_img_path, value=0.8, print_info=False, img=None):
        try:
            while True:
                if img is not None:
                    target_img = img
                else:
                    target_img = cv2_latest_image(self.image_buffer)
                find_img = cv2.imread(find_img_path)

                if target_img is None or find_img is None:
                    print(f"[Execution.find_templete] Failed to read images: target_img:{target_img is not None} find_img:{find_img is not None}")
                    return None, None

                best_match, best_val, best_loc = match_template(target_img, find_img)

                if best_val >= value:
                    if print_info :
                        print(f" Best match value: {best_val}")
                    return best_match, best_loc
                else:
                    continue
        except Exception as e:
            print(f"[Execution.find_templete] Error: {e}")
        return None, None
            
    def click_point(self,match,point):
        """
        点击指定的点。

        参数:
        match (numpy.ndarray): 匹配的图像区域。如果为 None，则只使用 point 参数。
        point (numpy.ndarray): 要点击的点坐标。如果 match 不为 None，则点击 match 的中心点加上 point 的偏移量。

        异常:
        如果 match 和 point 都为 None，打印错误信息。
        如果发生其他异常，打印错误信息。
        """
        try:
            if match is not None:
                if point is not None:
                    self.adbkit.click((point+np.array([match.shape[1]//2,match.shape[0]//2])))
                else:
                    print("[click_point] point is None")
            else:
                if point is not None:
                    self.adbkit.click(point)
                else:  
                    print("[click_point] match and point are None")
        except Exception as e:
            print(f"[click_point] Error: {e}")
    
    def swipe(self, start, end, duration=100):
        """
        模拟滑动操作。

        参数:
        start (tuple): 起始点坐标 (x, y)。
        end (tuple): 结束点坐标 (x, y)。
        duration (int, 可选): 滑动持续时间，默认为 100 毫秒。

        异常:
        如果发生异常，打印错误信息。
        """
        try:
            self.adbkit.swip(start,end,duration)
        except Exception as e:
            print(f"[swipe] Error: {e}")
            
    def send_key_event(self, keycode):
        """
        发送按键事件。

        参数:
        keycode (int): 按键代码。

        异常:
        如果发生异常，打印错误信息。
        """
        try:
            self.adbkit.send_key_event(keycode)
        except Exception as e:
            print(f"[send_key_event] Error: {e}")
    def wait_color(self, top_left, width, height, color,distance_threshold=70,print_info=False):
        """
        等待指定区域的颜色达到目标颜色。
        参数:
        top_left (tuple): 感兴趣区域的左上角坐标 (x, y)。
        width (int): 感兴趣区域的宽度。
        height (int): 感兴趣区域的高度。
        color (str): 目标颜色的十六进制字符串表示，例如 "#RRGGBB"。
        distance_threshold (int, 可选): 判断颜色相似度的距离阈值，默认为 50。
        print_info (bool, 可选): 是否打印调试信息并显示图像，默认为 False。
        返回:
        numpy.ndarray: 包含目标图像的数组，当检测到颜色相似时返回。
        内部函数:
        hex_to_rgb(hex_color): 将十六进制颜色转换为 RGB。
        color_distance(rgb1, rgb2): 计算两个 RGB 颜色之间的欧几里得距离。
        is_same_color_family_distance(hex1, hex2, distance_threshold): 判断两个十六进制颜色是否在指定距离阈值内。
        功能:
        1. 从图像缓冲区中获取最新图像。
        2. 提取指定区域 (ROI) 并计算其颜色均值。
        3. 将颜色均值转换为十六进制格式并与目标颜色进行比较。
        4. 如果颜色相似且 print_info 为 True，绘制矩形框并显示图像。
        5. 如果颜色相似，返回目标图像。
        """
        def hex_to_rgb(hex_color):
            # 将16进制颜色转换为RGB
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        def color_distance(rgb1, rgb2):
            # 计算RGB空间中的欧几里得距离
            return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))

        def is_same_color_family_distance(hex1, hex2,distance_threshold):
            rgb1 = hex_to_rgb(hex1)
            rgb2 = hex_to_rgb(hex2)
            
            # 计算RGB颜色距离
            distance = color_distance(rgb1, rgb2)
            
            # 判断距离是否小于阈值
            return distance <= distance_threshold
        while True:
            target_img = cv2_latest_image(self.image_buffer)
            # 获取左上角的坐标
            x, y = map(int, top_left)  # 将坐标转换为整数
            width = int(width)  # 将宽度转换为整数
            height = int(height)  # 将高度转换为整数
            
            # 提取感兴趣区域 (ROI)
            roi = target_img[y:y+height, x:x+width]
            
            # 计算该区域的颜色均值
            mean_color_bgr = cv2.mean(roi)[:3]  # 获取BGR通道的均值
            mean_color = mean_color_bgr[::-1]  # 转换为RGB格式
            
            # 将颜色均值转换为十六进制格式
            hex_color = "#{:02x}{:02x}{:02x}".format(int(mean_color[0]), int(mean_color[1]), int(mean_color[2]))
            is_same=is_same_color_family_distance(hex_color, color,distance_threshold)
            # if print_info:
            if is_same and print_info:
                # 使用最佳匹配绘制矩形框
                bottom_right = (x + width, y + height)
                middle_point = (x + width // 2, y + height // 2)
                # 保存图片
                save_path = 'latest_image.jpg'  # 指定保存路径
                cv2.imwrite(save_path, target_img)
                
                cv2.circle(target_img, middle_point, 5, (0, 0, 255), -1)
                cv2.rectangle(target_img, (x, y), bottom_right, (0, 255, 0), 2)

                target_img_rgb = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)
                plt.imshow(target_img_rgb)
                plt.axis('off')  # 隐藏坐标轴
                plt.show()
                
                print(f" mean_color: {mean_color} , {hex_color} , oragional  {color} , is_same: {is_same}")
                return target_img

            