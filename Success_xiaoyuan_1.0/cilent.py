import threading
import subprocess
import socket


from libs.execution import Execution
from time import sleep
import numpy as np
import json
# 设定分辨率
process = Execution()
info_ = False


def receive_data():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 9999))
    client_socket.settimeout(30.0)  # 设置超时时间为1秒

    try:
        while True:
            try:
                print("listening...")
                data = client_socket.recv(1024)
                if not data:
                    break
                print("Received:", data.decode())
                op(json.loads(data.decode()))
            except socket.timeout:
                
                continue  # 超时后继续循环
            except KeyboardInterrupt:
                print("\nConnection closed by user.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()


def op(list):
    print("等待进入答题界面")
    process.wait_templete("assests/xiaoyuan/4.png",0.8,print_info=info_)
    print('进入答题界面')
    # sleep(0.5)
    # input("any key to continue")
    speed=3
    for i in list:
        if i == "<":
            # (430, 1265) (, 1485) (815, 1545)
            process.swipe((687, 1447) , (555, 1525), speed)
            process.swipe( (555, 1525) ,(687, 1725) , speed)
        elif i == ">":
            process.swipe((555, 1447) , (687, 1525), speed)
            process.swipe( (687, 1525) ,(555, 1725) , speed)
        else:
            print('error',i)
        sleep(0.2)
    sleep(1.5)
    process.send_key_event(4)
    sleep(1.5)
    process.click_point(*process.find_templete("assests/xiaoyuan/5.png",0.8,print_info=info_))
    sleep(2.5)
    process.click_point(*process.find_templete("assests/xiaoyuan/3.png",0.8,print_info=info_))
    sleep(1.5)
    # process.click_point(*process.find_templete("assests/xiaoyuan/2.png",0.8,print_info=info_))
    # sleep(1.5)
    print("ending...listening for next round")




if __name__ == "__main__":
    receive_data()
    
    # adb forward tcp:1717 localabstract:minicap