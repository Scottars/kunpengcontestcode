#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time

exitFlag = 0


class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数



        print("Starting " + self.name)
        print_time(self.name, self.counter, 5)
        print("Exiting " + self.name)


def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            (threading.Thread).exit()
        time.sleep(delay)
        print( "%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1


# # 创建新线程
# thread1 = myThread(1, "Thread-1", 1)
# thread2 = myThread(2, "Thread-2", 2)
#
# # 开启线程
# thread1.start()
# thread2.start()
#
# print("Exiting Main Thread")
#
#
#
# import subprocess
# #cmd = 'cmd.exe c:\\sam.bat'
# p = subprocess.Popen("cmd.exe /c" + "c:\\sam.bat abc", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#
# curline = p.stdout.readline()
# while(curline != b''):
#     print(curline)
#     curline = p.stdout.readline()
#
# p.wait()
# print(p.returncode)

#
# def testnone(a):
#     if a is None:
#         print('a的确是None')
#         return None
#
#     print('测试是否执行这句话')
#
#
# for deep in range(0):
#     print('deep几层深度', deep)
#


for i in range(0):

    h=h-1
    if h==0:
        break
    print('h', h)
    print(i)