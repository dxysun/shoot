# -*- coding:utf-8 -*- 
__author__ = 'dxy'
import tkinter as tk
import subprocess
import os
import time
import threading
import tkinter.messagebox
import sys
import webbrowser

now_path = sys.path[0]
python_path = sys.path[2]
python_pre_path = os.path.abspath(os.path.dirname(python_path))
# 配置选项
PORT = 8000

p1 = None
manage_path = now_path + '\manage.py'
python_path = python_pre_path + '\python.exe'
shoot_cmd = '%s %s runserver %s' % (python_path, manage_path, PORT)
url_path = 'http://localhost:%d' % (PORT,)
print(shoot_cmd)


def start_browser():
    global p1
    p1 = subprocess.Popen(shoot_cmd)
    time.sleep(5)
    start_result.set("服务启动成功，打开浏览器访问射击大数据分析系统，访问地址：" + url_path)
    webbrowser.open_new_tab(url_path)
    print(p1.pid)


def start_server():
    print("start")
    close_result.set("")
    start_result.set("启动中")
    thread = threading.Thread(target=start_browser)
    thread.start()


def close_server():
    print("close")
    close_result.set("关闭中")
    if p1 is not None:
        res = os.system("taskkill /t /f /pid %s" % p1.pid)
        if res == 0:
            start_result.set("")
            close_result.set("服务器已关闭")
            print(p1.poll())
    else:
        print("p1 None")


def close_window():
    print('close')
    if p1 is not None:
        if p1.poll() == 1:
            return window.destroy()
        res = os.system("taskkill /t /f /pid %s" % p1.pid)
        if res == 0:
            return window.destroy()
        else:
            tk.messagebox.showwarning(title='警告', message='服务器未关闭，请关闭服务器后再关闭客户端')
    else:
        return window.destroy()


window = tk.Tk()
window.title('射击大数据分析系统客户端')
window.geometry('800x400')
window.protocol('WM_DELETE_WINDOW', close_window)
tk.Label(window, text='射击大数据分析系统客户端', font=('Microsoft YaHei', 12), width=30, height=2).pack()
tk.Button(window, text='启动服务器', font=('Microsoft YaHei', 15, 'bold'), width=15, height=1,
          command=start_server).pack()

tk.Label(window, text='', width=30, height=1).pack()

start_result = tk.StringVar()
tk.Label(window, textvariable=start_result).pack()

tk.Label(window, text='', width=30, height=1).pack()

tk.Button(window, text='关闭服务器', font=('Microsoft YaHei', 15, 'bold'), width=15, height=1, command=close_server).pack()

tk.Label(window, text='', width=30, height=1).pack()

close_result = tk.StringVar()
tk.Label(window, textvariable=close_result).pack()
window.mainloop()
