import cv2
import numpy as np
import mss

# 创建 mss 对象
with mss.mss() as sct:
    # 获取屏幕的尺寸
    monitor = sct.monitors[1]  # 选择第一个显示器，若有多个显示器可以调整索引

    # 只截取屏幕的右半部分
    monitor = {
        "top": monitor["top"],                # 保持顶部位置不变
        "left": monitor["left"] + monitor["width"] // 2,  # 设置左边界为屏幕中间
        "width": monitor["width"] // 2,       # 宽度为屏幕的一半
        "height": monitor["height"]           # 保持原始屏幕高度
    }

    while True:
        # 截取屏幕
        screen_shot = sct.grab(monitor)

        # 将捕获的图像转为 NumPy 数组，并将 BGRA 转换为 BGR（OpenCV 格式）
        img = np.array(screen_shot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 显示图像
        cv2.imshow('Right Half Screen', img)

        # 如果按下 'q' 键，退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放窗口资源
    cv2.destroyAllWindows()
