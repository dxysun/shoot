# -*- coding:utf-8 -*- 
__author__ = 'dxy'
import time
import random
import datetime
import threading
import math


def GeneratePointInCycle(r1, r2):
    theta = random.random() * 2 * math.pi
    r = random.uniform(r1, r2)
    y = math.sin(theta) * r
    x = math.cos(theta) * r
    return x, y


def generate_shoot_data(k=5):
    num = 0
    b = 0
    t = datetime.datetime.now()
    file_name = 'FILE_shoot_' + str(time.strftime('%Y_%m%d', time.localtime(time.time()))) + ".dat"
    print(file_name)
    while k > 0:
        grades = []
        sec = round(random.uniform(2, 2.5), 2)
        t1 = datetime.timedelta(seconds=sec)
        time.sleep(sec)
        t = t + t1
        b += 1
        sum1 = (num + 1) + 5 * b
        for i in range(0, 5):
            num += 1
            shoot_report_ctx = "%  " + str(sum1 - num) + "  §  "
            a = random.randint(1, 100)
            grade = random.randint(5, 10)
            x = 0
            y = 0
            if a % 2 == 0:
                shoot_report_ctx += str(grade) + "*" + "P " + str(t.strftime('%M:%S.%f')[:-4])
            else:
                shoot_report_ctx += str(grade) + " " + "P " + str(t.strftime('%M:%S.%f')[:-4])
            if random.randint(1, 1000) % 2 == 0:
                x = 1
            else:
                x = -1
            if random.randint(1, 1000) % 2 == 0:
                y = 1
            else:
                y = -1
            if grade == 10:
                x, y = GeneratePointInCycle(0, 50)
                x = round(x, 2)
                y = round(y, 2)
            if grade == 9:
                x, y = GeneratePointInCycle(50, 90)
                x = round(x, 2)
                y = round(y, 2)
            if grade == 8:
                x, y = GeneratePointInCycle(90, 130)
                x = round(x, 2)
                y = round(y, 2)
            if grade == 7:
                x, y = GeneratePointInCycle(130, 170)
                x = round(x, 2)
                y = round(y, 2)
            if grade == 6:
                x, y = GeneratePointInCycle(170, 210)
                x = round(x, 2)
                y = round(y, 2)
            if grade == 5:
                x, y = GeneratePointInCycle(210, 20)
                x = round(x, 2)
                y = round(y, 2)
            shoot_report_ctx += " " + str(x) + "/ " + " " + str(y)
            grades.append(shoot_report_ctx)
            grades.append("            (" + str(sec) + ")")
            s = round(random.uniform(0.5, 1.5), 2)
            sec = round(sec + s, 2)
            t1 = datetime.timedelta(seconds=s)
            time.sleep(s)
            t = t + t1
        t1 = datetime.timedelta(minutes=2)
        t = t + t1
        # print(grades)
        with open('D:/code/shoot/simulation_data/grade/' + file_name, 'a+', encoding='ISO-8859-15') as f:
            f.write("%Shot Report\n")
        for j in range(4, -1, -1):
            # print(grades[2 * j])
            # print(grades[2 * j + 1])
            con = grades[2 * j] + '\n'
            con += grades[2 * j + 1] + '\n'
            with open('D:/code/shoot/simulation_data/grade/' + file_name, 'a+', encoding='ISO-8859-15') as f:
                time.sleep(1)
                f.write(con)
        temp = "%   1  §  10*P 25:47.23  12.19/   9.08\n"
        temp += "            (4.05s)\n"
        with open('D:/code/shoot/simulation_data/grade/' + file_name, 'a+', encoding='ISO-8859-15') as f:
            time.sleep(1)
            f.write(temp)
        k -= 1


def generate_heart_data(t=5):
    while t > 0:
        file_name = "Heart" + str(time.strftime('%Y-%m-%d %H-%M-%S %A', time.localtime(time.time()))) + ".txt"
        print(file_name)
        t1 = 8 * 5
        context = ""
        while t1 > 0:
            time.sleep(0.2)
            heart_time = str(time.strftime('%H-%M-%S', time.localtime(time.time()))) + "：" + str(
                random.randint(40, 120))
            # print(heart_time)
            context += heart_time + "\n"
            t1 -= 1
        time.sleep(5)
        with open("D:/code/shoot/simulation_data/heart/" + file_name, 'w') as f:
            f.write(context)
        t -= 1


def generate_shake_data(t=5):
    while t > 0:
        file_name_x = "BesideX" + str(time.strftime('%Y-%m-%d %H-%M-%S %A', time.localtime(time.time()))) + ".txt"
        file_name_y = "BesideY" + str(time.strftime('%Y-%m-%d %H-%M-%S %A', time.localtime(time.time()))) + ".txt"
        print(file_name_x)
        t1 = 8 * 20
        context_x = ""
        context_y = ""
        while t1 > 0:
            time.sleep(0.05)
            shake_x = str(time.strftime('%H-%M-%S', time.localtime(time.time()))) + "：" + str(
                round(random.uniform(-1000, 2000), 3))
            shake_y = str(time.strftime('%H-%M-%S', time.localtime(time.time()))) + "：" + str(
                round(random.uniform(-1000, 2000), 3))
            # print(shake_x)
            context_x += shake_x + "\n"
            context_y += shake_y + "\n"
            t1 -= 1
        time.sleep(5)
        with open("D:/code/shoot/simulation_data/shake/x/" + file_name_x, 'w') as f:
            f.write(context_x)
        with open("D:/code/shoot/simulation_data/shake/y/" + file_name_y, 'w') as f:
            f.write(context_y)
        t -= 1


if __name__ == '__main__':
    print("thread start")
    # x, y = GeneratePointInCycle(50, 90)
    # print(x)
    # print(y)

    # generate_heart_data()
    # generate_shake_data()
    # generate_shoot_data()

    # print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    # t1 = datetime.timedelta(seconds=random.uniform(2, 2.5))
    # t = datetime.datetime.now() + t1
    # print(t.strftime('%Y-%m-%d %H:%M:%S.%f'))

    t1 = threading.Thread(target=generate_heart_data, args=(5,))
    t2 = threading.Thread(target=generate_shake_data, args=(5,))
    # t3 = threading.Thread(target=generate_shoot_data, args=(2,))
    t1.start()
    t2.start()
    # t3.start()
    print("thread end")
