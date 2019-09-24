'''
入口方法，选手不关注
'''
import sys
import threading
import time
import os
sys.path.append("..")
import  ballclient.service.constants as constants
from ballclient.comunicate import client

class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        print('开启进程threadid',threadID)


    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数

        maincode()



def maincode():
    # os.system('C:/Users/Scottar/Desktop/Contest/华为云鲲鹏开发者大赛-试题工程0801/试题工程/server/gameserver.bat')
    #用于本地的测试
    # os.system('C:/Users/Scottar/Desktop/Contest/华为云鲲鹏开发者大赛-试题工程0801/试题工程')
    # sys.argv = ['gameclient.bat', b'1515', b'127.0.0.1', b'6001']
    # sys.argv = ['gameclient.bat', b'1515', b'119.3.169.43', b'6001']
    # os.system('E:/Contest/华为云鲲鹏开发者大赛-试题工程0801/试题工程/run.bat')
    # sys.argv = ['gameclient.bat', b'1515', b'127.0.0.1', b'6001']
    # time.sleep(3)
    if len(sys.argv) != 4:
        print("The parameters has error. (TeamID server_ip server_port)")
        exit()
    team_id = sys.argv[1]
    server_ip = sys.argv[2]
    port = sys.argv[3]
    print("start client....................")
    print(team_id)
    print(server_ip)
    print(port)
    if team_id.isdigit() and port.isdigit():
        team_id = int(team_id)
        port = int(port)
    else:
        print("team_id and port must be digit.")
        exit()
    constants.team_id = team_id
    client.start(server_ip, port)


if __name__ == "__main__":
    print (sys.argv)
    # for i in range(100):
    #    maincode()
    #    time.sleep(0.5)

    maincode()

