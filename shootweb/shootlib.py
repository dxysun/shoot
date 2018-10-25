# -*- coding:utf-8 -*- 
import sys
import os
import datetime
import django
import time
import numpy as np
import math

sys.path.append('../shoot')
os.chdir('../shoot')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot.settings")
django.setup()
from shootweb.models import *


def get_max_five(x_data, y_data):
    xdata = {}
    ydata = {}
    i = 0
    for d in x_data:
        xdata[i] = d
        i += 1
    i = 0
    for y in y_data:
        ydata[i] = y
        i += 1
    x_top = sorted(xdata.items(), key=lambda x: x[1], reverse=True)
    x_top_five = dict(x_top[0:5])
    x_top_five = dict(sorted(x_top_five.items(), key=lambda x: x[0]))
    y_five = []
    for key in x_top_five.keys():
        y_five.append(ydata[key])
    return x_top_five.values(), y_five


def test():
    xData = [
        2.250, 0.250, 0.250, 0.000, 0.000, -0.250,
        0.000, 0.000, -0.250, 0.000, 0.000, -0.250, 0.000, 0.000, 0.000, 0.000, 0.250, 2.000, 0.500, 0.750, 0.500,
        0.250, 0.250, 0.250, 0.000, 0.000,
        0.000, 0.000, -0.250, 0.000, -0.250, 0.000, 0.000, -0.250, 0.000, 0.000, -0.250, 1.500, 0.750, 0.750, 0.750,
        0.250, 0.250, 0.000, 0.000, 0.000,
        -0.250, 0.000, 0.000, -0.250, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 1.500, 1.250, 1.000,
        0.500, 0.250, 0.250, 0.000, 0.000,
        0.000, 0.000, -0.250, 0.000, 0.250, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, -0.250, 0.000, 1.750,
        1.000, 0.500, 0.500, 0.250, 0.250,
        0.000, -0.250, -0.250, 0.000, -0.250, -0.250, 0.000, -0.500, -0.250, -0.750, -1.750, -1.750, -2.500, -18.750
    ]
    yData = [
        0.750, -0.500, -0.250, -0.500, -0.750, -0.750,
        -0.500, -0.500, -0.500, -0.500, -0.250, -0.250, 0.000, -0.250, -0.250, 0.250, 0.250, 4.250, 0.000, -0.250,
        0.500, 0.000, 0.000, 0.000, -0.250, -0.750,
        -0.250, -0.500, -0.750, -0.500, -0.500, -0.250, -0.250, -0.250, 0.250, 0.000, 0.000, 2.750, 1.250, -0.750,
        -0.250, -0.500, -0.500, -0.500, -0.500, -0.250,
        -0.250, 0.000, -0.500, 0.250, 0.000, 0.000, -0.250, 0.000, 0.000, 0.000, -0.250, -0.500, 3.000, 1.250, -0.250,
        0.250, -0.250, -0.750, -0.500, -0.250,
        -0.250, -0.500, 0.000, -0.250, -0.250, 0.000, 0.000, -0.250, 0.000, 0.000, -0.250, -0.250, 0.000, 0.000, 3.500,
        0.500, 0.250, 0.000, 0.000, -0.250,
        -0.250, -0.250, -0.750, -1.750, -1.000, -0.500, -0.500, 0.000, -0.250, -0.500, -2.250, -3.500, -11.500, 18.750,
    ]

    xs, ys = get_max_five(xData, yData)
    print(str(xs))
    print(str(ys))
    # for value in xs:
    #     print(value)
    # print()
    # for value in ys:
    #     print(value)


def get_shoot_info():
    reports = shoot_report.objects.all()
    shake_times = record_shake_time.objects.all()
    # heart_times = record_heart_time.objects.all()
    # for shake_time in shake_times:
    #     print(shake_time.record_date)
    #     timeArray = time.strptime(shake_time.record_date, "%Y-%m-%d %H:%M:%S")
    #     timestamp = time.mktime(timeArray)
    #     print(timestamp)
    context = ""
    for report in reports:
        record_start = time.strptime(report.shoot_date, "%Y-%m-%d %H:%M:%S")
        report_start_time = time.mktime(record_start)
        end_time = report.shoot_date[:-5] + report.end_time[:5]
        record_end = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        report_end_time = time.mktime(record_end)
        for shake_time in shake_times:
            record_start = time.strptime(shake_time.record_date, "%Y-%m-%d %H:%M:%S")
            record_start_time = time.mktime(record_start)
            if report_start_time < record_start_time < report_end_time:
                print(report.shoot_date)
                print(end_time)
                print(shake_time.record_date)
                shoot_grades = shoot_grade.objects.filter(report_id=report.id)
                shake_datas = shake_data.objects.filter(record_id=shake_time.id)
                x_data = []
                y_data = []
                for shakeData in shake_datas:
                    x_data += shakeData.x_data[:-1].split(",")
                    y_data += shakeData.y_data[:-1].split(",")
                x_data_five, y_data_five = get_max_five(x_data, y_data)
                x_data_five = list(x_data_five)
                print(len(shoot_grades))
                hearts = []
                data_info = ""
                i = 0
                for grade in shoot_grades:
                    data_info += grade.grade_date + "," + grade.grade + "," + grade.rapid_time + "," + grade.x_pos + "," + grade.y_pos + "," \
                                 + x_data_five[i] + "," + y_data_five[i] + ","
                    heart_times = heart_data.objects.filter(heart_date=grade.grade_date)
                    for heart_time in heart_times:
                        hearts.append(str(heart_time.average_rate))
                        data_info += str(heart_time.average_rate)
                    if len(heart_times) == 0:
                        data_info += "-1"
                    data_info += "\n"
                    i += 1
                print(data_info)
                context += data_info
                print(str(hearts))
                print(str(x_data_five))
                print(str(y_data_five))
                # heart_times = heart_data.objects.filter(heart_date=report.shoot_date)
                # for heart_time in heart_times:
                #     print(heart_time.heart_rate)
                print()
    with open("D:/workSpace/PythonWorkspace/shoot/shootweb/data/data.txt", 'w') as f:
        f.write(context)


def convert_x_y(x, y):
    if abs(x) <= 10:
        x = 0
    else:
        if x < 0:
            x = ((abs(x) - 10) / 40) * -1
        else:
            x = (x - 10) / 40
    if abs(y) <= 10:
        y = 0
    else:
        if y < 0:
            y = ((abs(y) - 10) / 40) * -1
        else:
            y = (y - 10) / 40
    return x, y


# 极坐标与直角坐标的关系：
# x=ρcos φ，y=ρsin φ
# 直角坐标与极坐标的关系：
# ρ²=x²+y²
# tan φ=y/x
def cart_to_polar(x, y):
    x, y = convert_x_y(x, y)
    z = pow(x, 2) + pow(y, 2)
    r = math.sqrt(z)
    angle = math.atan2(y, x) * 180 / math.pi
    if angle < 0:
        angle = 360 + angle
    r = round(r, 2)
    angle = round(angle, 2)
    # print(r)
    # print(11 - r)
    # print(angle)
    return r, angle


def update_report_data():
    shoot_reports = shoot_report.objects.all()
    for report in shoot_reports:
        print(report.remark)
        print(report.remark[6:8])
        report.remark = report.remark[6:8]
        report.save()


if __name__ == "__main__":
    print("shoot")
    # test()
    # get_shoot_info()
    # x1, y1 = - 36.06, -8.96
    # x2, y2 = 35.52, -7.48
    # x3, y3 = 2.96, 37.16
    # x4, y4 = - 32.49, 2.67
    # x5, y5 = - 26.68, -29.15
    # xs = [x1, x2, x3, x4, x5]
    # ys = [y1, y2, y3, y4, y5]

    # update_report_data()

