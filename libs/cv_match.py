import cv2
import numpy as np

def match_template(image, template,resize=False,gray=True):
    """
    在目标图像中匹配模板图像，支持多尺度匹配。
    参数:
    image (numpy.ndarray): 目标图像。
    template (numpy.ndarray): 模板图像。
    resize (bool): 是否进行多尺度匹配。默认为 False。
    返回:
    tuple: 包含最佳匹配的模板图像、最佳匹配值和最佳匹配位置的元组。
        - best_match (numpy.ndarray): 最佳匹配的模板图像。
        - best_val (float): 最佳匹配值。
        - best_loc (tuple): 最佳匹配位置 (x, y)。
    """

    # 转换为灰度图像
    if gray:
        target_img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        find_img_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    else:
        target_img_gray=image
        find_img_gray=template
    # 设置多尺度匹配的缩放范围
    scales = np.linspace(0.5, 1.5, 20)  # 设定从50%到150%的缩放比例
    best_match = None
    best_val = -1
    best_loc = None
    if resize:
        for scale in scales:
            # 缩放模板图像
            resized = cv2.resize(find_img_gray, (int(find_img_gray.shape[1] * scale), int(find_img_gray.shape[0] * scale)))

            # 如果缩放后的模板图像尺寸大于目标图像，跳过
            if resized.shape[0] > target_img_gray.shape[0] or resized.shape[1] > target_img_gray.shape[1]:
                continue

            # 在缩放后的图像上进行模板匹配
            result = cv2.matchTemplate(target_img_gray, resized, cv2.TM_CCOEFF_NORMED)

            # 获取最大匹配值及其位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 记录最佳匹配的结果
            if max_val > best_val:
                best_val = max_val
                best_match = resized
                best_loc = max_loc
    else:
        result = cv2.matchTemplate(target_img_gray, find_img_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        best_val = max_val
        best_match = find_img_gray
        best_loc= max_loc
    return best_match, best_val, best_loc