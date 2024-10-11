import socket
import sys
import time
import struct
from collections import OrderedDict
import os
import threading  # Import threading module
from PIL import Image  # Import PIL for image handling
import cv2
import numpy as np
import subprocess
import time
import os
import signal

class Banner:
    def __init__(self):
        self.__banner = OrderedDict(
            [('version', 0),
             ('length', 0),
             ('pid', 0),
             ('realWidth', 0),
             ('realHeight', 0),
             ('virtualWidth', 0),
             ('virtualHeight', 0),
             ('orientation', 0),
             ('quirks', 0)
             ])

    def __setitem__(self, key, value):
        self.__banner[key] = value

    def __getitem__(self, key):
        return self.__banner[key]

    def keys(self):
        return self.__banner.keys()

    def __str__(self):
        return str(self.__banner)


class Minicap:
    def __init__(self, host, port, banner):
        self.buffer_size = 4096
        self.host = host
        self.port = port
        self.banner = banner
        self.image_buffer = None

    def connect(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except (socket.error) as e:
            print(e)
            sys.exit(1)
        self.__socket.connect((self.host, self.port))

    def on_image_transfered(self, data):
        file_name = "temp/" + str(time.time()) + '.jpg'
        with open(file_name, 'wb') as f:
            f.write(data)
        self.manage_images()

    def manage_images(self):
        # List all .jpg files in the ./temp directory
        jpg_files = [f for f in os.listdir('./temp') if f.endswith('.jpg')]

        # Check if the number of images exceeds 10
        if len(jpg_files) > 10:
            # Sort files by modification time (oldest first)
            jpg_files.sort(key=lambda x: os.path.getmtime(os.path.join('./temp', x)))

            # Remove the oldest file
            oldest_file = jpg_files[0]
            os.remove(os.path.join('./temp', oldest_file))
            print(f"Removed oldest file: {oldest_file}")

    def consume(self, image_buffer):
        readBannerBytes = 0
        bannerLength = 24
        readFrameBytes = 0
        frameBodyLength = 0
        data = []
        while True:
            try:
                chunk = self.__socket.recv(self.buffer_size)
            except (socket.error) as e:
                print(e)
                sys.exit(1)
            cursor = 0
            buf_len = len(chunk)
            while cursor < buf_len:
                if readBannerBytes < bannerLength:
                    banner_data = struct.unpack("<2b5i2b", chunk[:bannerLength])
                    for i, key in enumerate(self.banner.keys()):
                        self.banner[key] = banner_data[i]
                    cursor = bannerLength
                    readBannerBytes = bannerLength
                    print(self.banner)
                elif readFrameBytes < 4:
                    frameBodyLength += (chunk[cursor] << (readFrameBytes * 8)) >> 0
                    cursor += 1
                    readFrameBytes += 1
                else:
                    if buf_len - cursor >= frameBodyLength:
                        data.extend(chunk[cursor:cursor + frameBodyLength])
                        image_buffer.add_image(bytes(data))
                        cursor += frameBodyLength
                        frameBodyLength = readFrameBytes = 0
                        data = []
                    else:
                        data.extend(chunk[cursor:buf_len])
                        frameBodyLength -= buf_len - cursor
                        cursor = buf_len


class ImageBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.index = 0

    def add_image(self, image):
        self.buffer[self.index] = image
        self.index = (self.index + 1) % self.size  # 循环覆盖

    def get_latest_image(self):
        return self.buffer[(self.index - 1) % self.size]  # 获取最新图片


def save_latest_image(buffer, filename):
    latest_image = buffer.get_latest_image()
    if latest_image is not None:
        with open(filename, 'wb') as f:
            f.write(latest_image)
        print(f"Saved latest image as {filename}")

def cv2_latest_image(buffer):
    latest_image = buffer.get_latest_image()
    if latest_image is not None:
        # 将字节数据转换为NumPy数组
        np_arr = np.frombuffer(latest_image, np.uint8)
        # 使用OpenCV从字节数据中读取图像
        cv2_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if cv2_img is not None:
            return cv2_img
        else:
            raise ValueError("Failed to decode image from buffer")
    return None
        
        

if '__main__' == __name__:


    # 启动 minicap 进程
    process = subprocess.Popen(
        ['adb', 'shell', 'LD_LIBRARY_PATH=/data/local/tmp', '/data/local/tmp/minicap', '-P', '1080x2400@1080x2400/0'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # 等待一段时间以确保 minicap 正在运行
    time.sleep(1)
    mc = Minicap('localhost', 1717, Banner())
    mc.connect()

    buffer_size = 5  # 缓冲区大小
    image_buffer = ImageBuffer(buffer_size)

    # Create a thread for the consume method
    consume_thread = threading.Thread(target=mc.consume, args=(image_buffer,))
    consume_thread.daemon = True  # Set the thread as a daemon thread
    consume_thread.start()  # Start the thread

    try:
        while True:
            input("Press any key to print\n")
            save_latest_image(image_buffer, "latest_image.jpg")
            cv2_img=cv2_latest_image(image_buffer)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # 在程序退出前终止进程
        process.terminate()  # 或者 process.kill()
        print("minicap终止")