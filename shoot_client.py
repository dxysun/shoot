# -*- coding:utf-8 -*- 
__author__ = 'dxy'
import tkinter as tk
import subprocess
import os
import time
import threading
import tkinter.messagebox
import webbrowser
import configparser
import sys

dirname, filename = os.path.split(os.path.abspath(__file__))
print(dirname)
conf = configparser.ConfigParser()

window = tk.Tk()
window.title('射击大数据分析系统客户端')
window.geometry('800x400')

if os.path.exists(dirname + '/shoot_config.ini'):
    conf.read(dirname + '/shoot_config.ini')
else:
    tk.messagebox.showwarning(title='警告',
                              message='请设置客户端程序同一目录下shoot_config.ini中的python路径python_path和射击大数据系统的服务器路径shoot_path')
    with open(dirname + '/shoot_config.ini', 'w') as shoot_file:
        shoot_file.write("[shoot_setting]\n")
    conf.read(dirname + '/shoot_config.ini')
    conf.set('shoot_setting', 'python_path', "")
    conf.set('shoot_setting', 'shoot_path', "")
    conf.write(open(dirname + '/shoot_config.ini', "w"))
    sys.exit()

python_path = conf.get('shoot_setting', 'python_path')
shoot_path = conf.get('shoot_setting', 'shoot_path')
if python_path == "" or shoot_path == "":
    tk.messagebox.showwarning(title='警告',
                              message='请设置客户端程序同一目录下shoot_config.ini中的python路径python_path和射击大数据系统的服务器路径shoot_path')
    sys.exit()
manage_path = shoot_path + '/manage.py'

PORT = 8000

p1 = None

shoot_cmd = '%s %s runserver %s' % (python_path, manage_path, PORT)
url_path = 'http://localhost:%d' % (PORT,)
print(shoot_cmd)


def start_browser():
    global p1
    p1 = subprocess.Popen(shoot_cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(5)
    start_result.set("服务启动成功，打开浏览器访问射击大数据分析系统，访问地址：" + url_path + "/shoot")
    webbrowser.open_new_tab(url_path)
    print(p1.pid)


def start_server():
    print("start")
    if p1 is not None:
        if p1.poll() is None:
            tk.messagebox.showwarning(title='警告', message='服务器已启动')
            return
    close_result.set("")
    start_result.set("启动中")
    thread0 = threading.Thread(target=progress)
    thread0.start()
    thread = threading.Thread(target=start_browser)
    thread.start()


def kill_process():
    p2 = subprocess.Popen("taskkill /t /f /pid %s" % p1.pid, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    p2.wait()
    close_result.set("服务器已关闭")


def close_server():
    print("close")
    if p1 is not None:
        if p1.poll() is None:
            close_result.set("关闭中")
            start_result.set("")
            canvas.pack_forget()
            thread1 = threading.Thread(target=kill_process)
            thread1.start()
    else:
        print("p1 None")
        tk.messagebox.showwarning(title='警告', message='服务器未启动')


def close_window():
    print('close')
    if p1 is not None:
        print(p1.poll())
        if p1.poll() == 1 or p1.poll() == 2:
            return window.destroy()
        res = os.system("taskkill /t /f /pid %s" % p1.pid)
        if res == 0:
            return window.destroy()
        else:
            tk.messagebox.showwarning(title='警告', message='服务器未关闭，请关闭服务器后再关闭客户端')
    else:
        return window.destroy()


# 显示下载进度
def progress():
    # 清空进度条
    fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="white")
    x = 250  # 未知变量，可更改
    n = 465 / x  # 465是矩形填充满的次数

    for t in range(x):
        n = n + 465 / x
        # 以矩形的长度作为变量值更新
        canvas.coords(fill_line, (0, 0, n, 60))
        window.update()

    # 填充进度条
    canvas.pack(after=start)
    fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
    x = 250  # 未知变量，可更改
    n = 465 / x  # 465是矩形填充满的次数
    for i in range(x):
        n = n + 465 / x
        canvas.coords(fill_line, (0, 0, n, 60))
        window.update()
        time.sleep(0.02)  # 控制进度条流动的速度


window.protocol('WM_DELETE_WINDOW', close_window)
tk.Label(window, text='射击大数据分析系统客户端', font=('Microsoft YaHei', 12), width=30, height=2).pack()
start = tk.Button(window, text='启动服务器', font=('Microsoft YaHei', 15, 'bold'), width=15, height=1,
                  command=start_server)
start.pack()

# tk.Label(window, text='', width=30, height=1).pack()
# 设置下载进度条
# tk.Label(window, text='下载进度:', ).place(x=50, y=60)
canvas = tk.Canvas(window, width=465, height=22, bg="white")
canvas.pack_forget()

start_result = tk.StringVar()
tk.Label(window, textvariable=start_result).pack()

tk.Label(window, text='', width=30, height=1).pack()

tk.Button(window, text='关闭服务器', font=('Microsoft YaHei', 15, 'bold'), width=15, height=1, command=close_server).pack()

tk.Label(window, text='', width=30, height=1).pack()

close_result = tk.StringVar()
tk.Label(window, textvariable=close_result).pack()
window.mainloop()
