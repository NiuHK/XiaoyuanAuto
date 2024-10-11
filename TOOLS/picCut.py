import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageGrab
from libs.adb import adbKit
import numpy as np

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")

        # 加载图像
        self.image_path = 'screencap.png'
        self.original_image = Image.open(self.image_path)

        # 计算缩放比例
        self.scale_ratio = 0.2
        self.display_image = self.original_image.resize(
            (int(self.original_image.width * self.scale_ratio), int(self.original_image.height * self.scale_ratio)),
            Image.LANCZOS
        )
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        # 创建Canvas显示图片
        self.canvas = tk.Canvas(self.root, width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # 初始化选择框
        self.rect = None
        self.start_x = None
        self.start_y = None

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_button_press)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_button_release)
        self.canvas.bind("<B3-Motion>", self.on_right_button_drag)

    def on_button_press(self, event):
        # 记录点击开始的坐标
        self.start_x = event.x
        self.start_y = event.y
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_mouse_drag(self, event):
        # 画框时动态更新矩形框的大小
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        # 获取选择区域并裁剪
        end_x, end_y = event.x, event.y
        self.crop_and_save_image(self.start_x, self.start_y, end_x, end_y)

    def on_right_button_press(self, event):
        # 记录右键点击开始的坐标
        self.start_x = event.x
        self.start_y = event.y
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="blue", width=2)

    def on_right_button_drag(self, event):
        # 右键画框时动态更新矩形框的大小
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_right_button_release(self, event):
        # 获取右键选择区域并计算颜色均值
        end_x, end_y = event.x, event.y
        self.calculate_and_output_mean_color(self.start_x, self.start_y, end_x, end_y)

    def calculate_and_output_mean_color(self, x1, y1, x2, y2):
        # 确保坐标正确
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        x2=x1+1 
        y2=y1+1

        # 将框选区域坐标映射到原始图像
        crop_box = (int(x1 / self.scale_ratio), int(y1 / self.scale_ratio), int(x2 / self.scale_ratio), int(y2 / self.scale_ratio))
        cropped_image = self.original_image.crop(crop_box)

        # 转换为numpy数组以计算颜色均值
        cropped_array = np.array(cropped_image)
        mean_color = tuple(cropped_array.mean(axis=(0, 1)))

        # 输出框的长、宽、左上角顶点的元组和颜色均值
        width = int((x2 - x1)/self.scale_ratio)
        height = int((y2 - y1)/self.scale_ratio)
        top_left = (int(x1/self.scale_ratio), int(y1/self.scale_ratio))
        hex_color = "#{:02x}{:02x}{:02x}".format(int(mean_color[0]), int(mean_color[1]), int(mean_color[2]))
        print(f"左上角顶点,框的长宽w/h: {top_left},{width},{height}  , 颜色均值: {mean_color},{hex_color}")
        print(f"process.wait_color({top_left},{width},{height},'{hex_color}')\n")

    def crop_and_save_image(self, x1, y1, x2, y2):
        # 确保坐标正确
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # 将框选区域坐标映射到原始图像
        crop_box = (int(x1 / self.scale_ratio), int(y1 / self.scale_ratio), int(x2 / self.scale_ratio), int(y2 / self.scale_ratio))
        cropped_image = self.original_image.crop(crop_box)

        # 保存裁剪的图像
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if save_path:
            cropped_image.save(save_path)
            print(f"裁剪的图像已保存为: {save_path}")

if __name__ == "__main__":
    print("""
          左键截图
          右键则算颜色
            取颜色的时候，只取一个像素(大概是1*1的区域(还是2*2来着?))
          """)
    adb = adbKit()
    adb.screenshots()
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
    
    
    
    
    