import ffmpeg
import cv2
import numpy as np

# 定义视频流地址
stream_url = 'tcp://localhost:1234'

# 获取视频流的宽度和高度
probe = ffmpeg.probe(stream_url)
video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
width = int(video_info['width'])
height = int(video_info['height'])

# 使用 ffmpeg 读取视频流
process = (
    ffmpeg
    .input(stream_url, flags='low_delay', f='h264')
    .output('pipe:', format='rawvideo', pix_fmt='bgr24', vf='setpts=0')
    .run_async(pipe_stdout=True)
)

while True:
    # 从视频流中读取一帧
    in_bytes = process.stdout.read(width * height * 3)
    if not in_bytes:
        break

    # 将字节数据转换为 NumPy 数组
    frame = (
        np
        .frombuffer(in_bytes, np.uint8)
        .reshape([height, width, 3])
    )

    # 使用 OpenCV 展示视频帧
    cv2.imshow('Video', frame)

    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
process.stdout.close()
cv2.destroyAllWindows()