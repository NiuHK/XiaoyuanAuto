# Android Auto Automation

本项目旨在通过自动化工具实现对 Android 设备的截图、图像裁剪、颜色计算和模板匹配等操作。项目使用了 Python 语言，并结合了 OpenCV、PIL 和 ADB 等工具。

## 安装依赖

在运行本项目之前，请确保已安装依赖：

```sh
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

## 使用方法

### 1. 将 minicap 传到手机上并赋权限

```
adb push minicap /data/local/tmp
adb push minicap.so /data/local/tmp
adb shell chmod 777 /data/local/tmp/minicap
adb shell chmod 777 /data/local/tmp/minicap.so
```

### 2. 测试 minicap 是否可运行

```
adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1080x2160@1080x2160/0 -t
```

3. 启动服务

```
adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1080x2400@1080x2400/0
adb forward tcp:1717 localabstract:minicap
```

### 4. 运行主程序

在 `main.ipynb` 中含有示例代码.

首先初始化运行环境,链接minicap:

```python
from libs.execution import Execution
process = Execution()
```

之后可运行目标匹配等:

```python
process.click_point(*process.find_templete("assets/xiaoyuan/1.png", 0.8, print_info=True))
#目标匹配并点击
process.wait_color((57, 117), 2, 2, '#f9b842', print_info=True)
#等待某处颜色更新,用来等待加载动画
process.click_point(*process.find_templete("assets/xiaoyuan/2.png", 0.8, print_info=True))
```

## 文件说明

### `libs/adb.py`

该文件封装了 ADB 的一些常用操作，如截图和点击。

### `libs/cv_match.py`

该文件实现了模板匹配功能，使用 OpenCV 进行图像处理和匹配。

### `libs/execution.py`

该文件封装了自动化执行的主要逻辑，包括启动 minicap 服务、模板匹配、点击操作和颜色等待等功能。

### `libs/minicap.py`

该文件实现了 minicap 的连接和图像处理功能。

## 开发工具

### `TOOLS/picCut.py`

为提升识别速度,设置为固定大小进行模板匹配,因此需使用该脚本进行原分辨率截图, 才能保证识别效果

### `TOOLS/colorTest.ipynb`

在颜色识别中,使用RGB欧几里得距离取值限制进行相似颜色检验,该脚本用来获取验证某颜色的符合条件的相近颜色,但是好像是有问题.

## 贡献

欢迎提交 issue 和 pull request 来改进本项目。

## 许可证

本项目采用 MIT 许可证。


## 版本控制

| VERSION | FIX             | TODO                                                              |
| ------- | --------------- | ----------------------------------------------------------------- |
| 1.0     | 未加密版本,可行 | 适配新版加密<br />生产消费者模式代替套接字<br />scrcpy代替minicap |
|         |                 |                                                                   |
