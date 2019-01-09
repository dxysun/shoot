# -*- coding:utf-8 -*- 
import sys
import os
import datetime
import django
import time
import math
import pandas as pd
import shootlib
from scipy.interpolate import interp1d
import numpy as np

dirname, filename = os.path.split(os.path.abspath(__file__))
pre_path = os.path.abspath(os.path.dirname(dirname))
sys.path.append(pre_path + '/shoot')
os.chdir(pre_path + '/shoot')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot.settings")
django.setup()
from shootweb.models import *


# 把datetime转成字符串
def time_to_string(dt):
    return dt.strftime("%H:%M:%S")


def time_to_string_mill(dt):
    return dt.strftime("%H:%M:%S.%f")


# 把字符串转成datetime
def string_to_time(string):
    return datetime.datetime.strptime(string, "%H:%M:%S")


# 把字符串转成datetime
def string_to_time_mill(string):
    return datetime.datetime.strptime(string, "%H:%M:%S.%f")


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


def get_all_shoot_info():
    reports = shoot_report.objects.all()
    shake_times = record_shake_time.objects.all()
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


def polar_to_cart(x, y, r):
    x_data = []
    y_data = []
    x_start = x + r * math.cos(0 * math.pi / 180)
    y_start = y + r * math.sin(0 * math.pi / 180)
    for angle in range(0, 360):
        x1 = x + r * math.cos(angle * math.pi / 180)
        y1 = y + r * math.sin(angle * math.pi / 180)
        x_data.append(round(x1, 2))
        y_data.append(round(y1, 2))
    x_data.append(x_start)
    y_data.append(y_start)
    return x_data, y_data


def update_shoot_report():
    # shoot_reports = shoot_report.objects.filter(user_name="C")
    shoot_reports = shoot_report.objects.all()
    for report in shoot_reports:
        print(report.shoot_date)
        print(report.start_time)
        # if report.is_process == 2:
        #     report.delete()

        # grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
        # rapid_time = grades[4].rapid_time
        # stage = 8
        # if float(rapid_time) < 1:
        #     print(grades[3].rapid_time)
        #     if float(grades[3].rapid_time) < 4:
        #         stage = 4
        #     elif float(grades[3].rapid_time) < 6:
        #         stage = 6
        #     elif float(grades[3].rapid_time) < 8:
        #         stage = 8
        # elif float(rapid_time) < 4.2:
        #     stage = 4
        # elif float(rapid_time) < 6.2:
        #     stage = 6
        # elif float(rapid_time) < 8:
        #     stage = 8
        # print(rapid_time)
        # print()
        # report.remark = str(stage)
        # report.save()
        # report_time = time_to_string_mill(
        #     string_to_time_mill(report.start_time) - datetime.timedelta(seconds=float(rapid_time)))
        # print(report_time[:-4])
        # report.shoot_time = report.start_time
        # report.start_time = report_time[:-4]
        # report.save()

        # for grade in grades:
        #     print(grade.rapid_time)
        #     print(grade.grade_detail_time)
        # grade.grade_time = grade.grade_detail_time[:-3]
        # print(grade.grade_detail_time[:-3])
        # grade.delete()
        # grade.save()
        # report.delete()


def update_shoot_grade():
    shoot_grades = shoot_grade.objects.all()
    for grade in shoot_grades:
        print(grade.grade_date)
        if grade.grade_date == '2018-11-29':
            grade.delete()
        # grade.grade_detail_time = grade.grade_time
        # grade.grade_time = grade.grade_date[-8:]
        # grade.grade_date = grade.grade_date[:-9]
        # grade.user_name = "A"
        # grade.save()


def update_shake_time():
    record_shake_times = record_shake_time.objects.all()
    for shake_time in record_shake_times:
        # if shake_time.record_time < '15:24:00':
        #     print(shake_time.record_time)
        #     record_time = string_to_time(shake_time.start_time)
        #     shake_time.start_time = time_to_string(record_time - datetime.timedelta(minutes=3, seconds=21))
        #     record_time = string_to_time(shake_time.end_time)
        #     shake_time.end_time = time_to_string(record_time - datetime.timedelta(minutes=3, seconds=21))
        #     shake_time.record_time = shake_time.start_time
        #     shake_time.save()

        start_time = string_to_time(shake_time.start_time)
        end_time = string_to_time(shake_time.end_time)
        if end_time - start_time < datetime.timedelta(seconds=4):
            print(shake_time.start_time)
            print(shake_time.end_time)
            print()
            shake_time.delete()

        # x_data = ""
        # y_data = ""
        # shake_datas = shake_data.objects.filter(record_id=shake_time.id)
        # x_data_detail = ""
        # y_data_detail = ""
        # for shakeData in shake_datas:
        #     x_data += shakeData.x_data
        #     y_data += shakeData.y_data
        #     t = shakeData.shake_time.replace(":", "-")
        #     x_data_detail += t + ":"
        #     x_data_detail += shakeData.x_data + "\n"
        #     y_data_detail += t + ":"
        #     y_data_detail += shakeData.y_data + "\n"
        # shake_time.shake_x_data = x_data[:-1]
        # shake_time.shake_y_data = y_data[:-1]
        # shake_time.shake_x_detail_data = x_data_detail
        # shake_time.shake_y_detail_data = y_data_detail
        # shake_time.is_process = 1
        # shake_time.user_name = "A"
        # shake_time.save()


def update_shake_data():
    shake_datas = shake_data.objects.all()
    for data in shake_datas:
        print(data.shake_date)
        data.shake_time = data.shake_date[-8:]
        data.shake_date = data.shake_date[:-9]
        data.save()


def update_heart_time():
    record_heart_times = record_heart_time.objects.all()
    for heart_time in record_heart_times:
        print(heart_time.record_date)
        # heart_time.record_time = heart_time.record_date[-8:]
        # heart_time.record_date = heart_time.record_date[:-9]
        # heart_time.is_process = 1
        # heart_time.user_name = "A"
        # heart_time.save()


def update_heart_data():
    heart_datas = heart_data.objects.all()
    for data in heart_datas:
        if data.average_rate == 0:
            print(data.heart_time)
        # data.heart_time = data.heart_date[-8:]
        # data.heart_date = data.heart_date[:-9]
        # data.user_name = "A"
        # data.save()


def update_all_info():
    shoot_reports = shoot_report.objects.filter(is_process=0)
    for report in shoot_reports:
        shake_times = record_shake_time.objects.all(is_process=0)
        record_start = time.strptime(report.shoot_date + " " + report.shoot_time, "%Y-%m-%d %H:%M:%S")
        report_start_time = time.mktime(record_start)
        end_time = report.shoot_date + " " + report.shoot_time[:3] + report.end_time[:5]
        record_end = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        report_end_time = time.mktime(record_end)
        x_data = ""
        y_data = ""
        grades = ""
        hearts = ""
        r_pos = ""
        p_pos = ""
        x_data_five = []
        y_data_five = []
        for shake_time in shake_times:
            record_start = time.strptime(shake_time.record_date + " " + shake_time.record_time, "%Y-%m-%d %H:%M:%S")
            record_start_time = time.mktime(record_start)
            if report_start_time <= record_start_time <= report_end_time:
                # shake_datas = shake_data.objects.filter(record_id=shake_time.id)
                x_data += shake_time.shake_x_data
                y_data += shake_time.shake_y_data
                x_datas = shake_time.shake_x_data.split(",")
                y_datas = shake_time.shake_y_data.split(",")
                # for shakeData in shake_datas:
                #     x_data += shakeData.x_data
                #     y_data += shakeData.y_data
                #     x_datas += shakeData.x_data[:-1].split(",")
                #     y_datas += shakeData.y_data[:-1].split(",")
                x_data_five, y_data_five = get_max_five(x_datas, y_datas)
                x_data_five = list(x_data_five)
                shake_time.is_process = 1
                shake_time.save()
        report.x_shake_data = x_data
        report.y_shake_data = y_data
        shoot_grades = shoot_grade.objects.filter(report_id=report.id)
        i = 0
        is_have_shake = True
        if len(x_data_five) == 0:
            is_have_shake = False
        for grade in shoot_grades:
            if is_have_shake:
                grade.x_shake = float(x_data_five[i])
                grade.y_shake = float(y_data_five[i])
            else:
                grade.x_shake = 0
                grade.y_shake = 0
            grades += grade.grade + ","
            x = float(grade.x_pos)
            y = float(grade.y_pos)
            r, p = cart_to_polar(x, y)
            r = 11 - r
            r_pos += str(r) + ","
            p_pos += str(p) + ","
            heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
            if len(heart_times) == 1:
                heart_time = heart_times[0]
                grade.heart_rate = heart_time.average_rate
                hearts += str(heart_time.average_rate) + ","
            else:
                grade.heart_rate = 0
                hearts += "0,"
            grade.save()
            i += 1
        report.is_process = 1
        report.save()


def update_grade_heart_info():
    grades = shoot_grade.objects.filter(user_name="A").filter(grade_date="2018-12-20")
    # grades = shoot_grade.objects.all()
    for grade in grades:
        grade_time = time_to_string(string_to_time(grade.grade_time) + datetime.timedelta(seconds=7))
        heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade_time)
        if len(heart_times) >= 1:
            print(grade.grade_time)
            heart_time = heart_times[0]
            grade.heart_rate = heart_time.average_rate
        else:
            print(grade.grade_time + ':no data')
            grade.heart_rate = None
        grade.save()
        # if grade.heart_rate == 0 or grade.heart_rate is None:
        #     heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
        #     if len(heart_times) >= 1:
        #         print(grade.grade_time)
        #         heart_time = heart_times[0]
        #         grade.heart_rate = heart_time.average_rate
        #     else:
        #         print(grade.grade_time + ':no data')
        #         grade.heart_rate = None
        #     grade.save()

        # if len(grade.grade_detail_time) > 13:
        #     print(grade.grade_detail_time)
        #     print(grade.grade_detail_time[:8])
        #     print(grade.grade_detail_time[-3:])
        #     grade.grade_detail_time = grade.grade_detail_time[:8] + grade.grade_detail_time[-3:]
        #     grade.save()
        #     print()

        # if grade.heart_rate == 0:
        #     print(grade.grade_time)
        # heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
        # if len(heart_times) >= 1:
        #     print(grade.grade_time)
        #     heart_time = heart_times[0]
        #     grade.heart_rate = heart_time.average_rate
        # else:
        #     print('no data')
        #     grade.heart_rate = 0
        # grade.save()


def update_report_shake_info():
    # shoot_reports = shoot_report.objects.filter(is_process=0).filter(user_name="B")
    shoot_reports = shoot_report.objects.all()
    print(len(shoot_reports))
    for report in shoot_reports:
        report.total_grade = float(report.remark)
        report.remark = ""
        report.save()
        # report_time = time_to_string(string_to_time(report.shoot_time[:-3]) + datetime.timedelta(seconds=2))
        # shake_times = shake_all_info.objects.filter(start_time__lte=report_time).filter(end_time__gte=report_time)
        # if len(shake_times) == 1:
        #     print('find ' + report.shoot_time)
        #     shake = shake_times[0]
        #     report.x_shake_data = shake.beside_x_data
        #     report.y_shake_data = shake.beside_y_data
        #     report.x_shake_pos = shake.beside_x_pos
        #     report.y_shake_pos = shake.beside_y_pos
        #     report.x_up_shake_data = shake.up_x_data
        #     report.y_up_shake_data = shake.up_y_data
        #     report.x_up_shake_pos = shake.up_x_pos
        #     report.y_up_shake_pos = shake.up_y_pos
        #     report.is_process = 1
        #     # shake.is_process = report.id
        #     # up_shake.is_process = report.id
        #     # shake.save()
        #     # up_shake.save()
        #     report.save()
        # else:
        #     print('not find ' + report.shoot_time)


def process_shake_data():
    shake_datas = record_shake_time.objects.filter(user_name="A")
    for data in shake_datas:
        # record_time = time_to_string(string_to_time(data.record_time) + datetime.timedelta(seconds=1))
        record_time = data.record_time
        report_times = shoot_report.objects.filter(user_name="B").filter(start_time__lte=record_time).filter(
            end_time__gte=record_time)
        if len(report_times) > 0:
            print(data.record_time)
            print(len(report_times))
            print(report_times[0].shoot_time)
            print()
            if string_to_time(data.end_time) - string_to_time(data.start_time) <= datetime.timedelta(seconds=2):
                print("delete " + data.record_time)
                data.delete()
        else:
            print(data.record_time + "  not find data")
            data.delete()

    print("up_data")
    shake_up_datas = record_up_shake_time.objects.filter(user_name="B")
    for data in shake_up_datas:
        # record_time = time_to_string(string_to_time(data.record_time) + datetime.timedelta(seconds=1))
        record_time = data.record_time
        report_times = shoot_report.objects.filter(user_name="B").filter(start_time__lte=record_time).filter(
            end_time__gte=record_time)
        if len(report_times) > 0:
            print(data.record_time)
            print(len(report_times))
            print(report_times[0].shoot_time)
            print()
            if string_to_time(data.end_time) - string_to_time(data.start_time) <= datetime.timedelta(seconds=2):
                print("delete " + data.record_time)
                data.delete()
        else:
            print(data.record_time + "  not find data")
            data.delete()


def process_shake_time_data():
    shake_datas = record_shake_time.objects.filter(user_name="B")
    for data in shake_datas:
        up_data = record_up_shake_time.objects.filter(is_process=data.is_process)
        up_data = up_data[0]
        beside_shake = data.remark.strip("\n").split("\n")
        up_shake = up_data.remark.strip("\n").split("\n")
        beside_first = beside_shake[0].split(":")
        up_first = up_shake[0].split(":")

        if string_to_time(data.start_time) >= string_to_time(up_data.start_time):
            if string_to_time(data.start_time) == string_to_time(up_data.start_time):
                if int(up_first[3]) >= int(beside_first[3]):
                    line = 0
                    for shake in beside_shake:
                        shake_info = shake.split(":")
                        if shake_info[0] == up_first[0] and shake_info[1] == up_first[1] and shake_info[2] == up_first[
                            2]:
                            if abs(int(shake_info[3]) - int(up_first[3])) <= 10:
                                break
                        line += 1
                    beside_shake = beside_shake[line:]
                else:
                    line = 0
                    for shake in up_shake:
                        shake_info = shake.split(":")
                        if shake_info[0] == beside_first[0] and shake_info[1] == beside_first[1] and shake_info[2] == \
                                beside_first[2]:
                            if abs(int(shake_info[3]) - int(beside_first[3])) <= 10:
                                break
                        line += 1
                    up_shake = up_shake[line:]
            else:
                line = 0
                for shake in up_shake:
                    shake_info = shake.split(":")
                    if shake_info[0] == beside_first[0] and shake_info[1] == beside_first[1] and shake_info[2] == \
                            beside_first[2]:
                        if abs(int(shake_info[3]) - int(beside_first[3])) <= 10:
                            break
                    line += 1
                up_shake = up_shake[line:]
        else:
            line = 0
            for shake in beside_shake:
                shake_info = shake.split(":")
                if shake_info[0] == up_first[0] and shake_info[1] == up_first[1] and shake_info[2] == up_first[2]:
                    if abs(int(shake_info[3]) - int(up_first[3])) <= 10:
                        break
                line += 1
            beside_shake = beside_shake[line:]
        if len(up_shake) > len(beside_shake):
            up_shake = up_shake[:len(beside_shake)]
        if len(up_shake) < len(beside_shake):
            beside_shake = beside_shake[:len(up_shake)]
        # print(len(up_shake))
        # print(len(beside_shake))
        print(up_shake[0])
        print(beside_shake[0])
        # print(up_shake[-1])
        # print(beside_shake[-1])
        print()
        beside_remark = ""
        up_remark = ""
        shake_x_data = ""
        shake_x_detail_data = ""
        shake_y_data = ""
        shake_y_detail_data = ""
        up_shake_x_data = ""
        up_shake_x_detail_data = ""
        up_shake_y_data = ""
        up_shake_y_detail_data = ""
        for beside, up in zip(beside_shake, up_shake):
            beside_remark += beside + "\n"
            up_remark += up + "\n"
            beside = beside.split(":")
            beside = beside[-1]
            beside = beside.split("#")
            shake_x_detail_data += beside[0] + ","
            shake_y_detail_data += beside[1] + ","
            shake_x_data += beside[2] + ","
            shake_y_data += beside[3] + ","
            up = up.split(":")
            up = up[-1]
            up = up.split("#")
            up_shake_x_detail_data += up[0] + ","
            up_shake_y_detail_data += up[1] + ","
            up_shake_x_data += up[2] + ","
            up_shake_y_data += up[3] + ","
        data.remark = beside_remark
        data.shake_x_detail_data = shake_x_detail_data[:-1]
        data.shake_y_detail_data = shake_y_detail_data[:-1]
        data.shake_x_data = shake_x_data[:-1]
        data.shake_y_data = shake_y_data[:-1]
        data.save()
        up_data.remark = up_remark
        up_data.shake_x_detail_data = up_shake_x_detail_data[:-1]
        up_data.shake_y_detail_data = up_shake_y_detail_data[:-1]
        up_data.shake_x_data = up_shake_x_data[:-1]
        up_data.shake_y_data = up_shake_y_data[:-1]
        up_data.save()


def process_null_heart():
    shoot_reports = shoot_report.objects.all()
    print(len(shoot_reports))

    heart_null_count = 0
    for report in shoot_reports:
        shoot_grades = shoot_grade.objects.filter(report_id=report.id)
        null_grade = []
        sum_heart = 0
        sum_len = 0
        for grade in shoot_grades:
            # print(grade.grade_detail_time)
            if grade.heart_rate is None or grade.heart_rate == 0:
                print(grade.grade_date + " " + grade.grade_detail_time)
                print('grade heart_rate null')
                heart_null_count += 1
                null_grade.append(grade)
            else:
                sum_heart += grade.heart_rate
                sum_len += 1
        if len(null_grade) > 0:
            heart_average = int(sum_heart / sum_len)
            for g in null_grade:
                g.heart_rate = heart_average
                g.save()
        # print()
    print('heart_null_count:' + str(heart_null_count))


def save_report_info():
    shoot_reports = shoot_report.objects.all()
    print(len(shoot_reports))
    report_df = pd.DataFrame(columns=['id', 'shoot_date', 'shoot_time', 'start_time', 'end_time', 'total_grade',
                                      'stage', 'x_shake_data', 'y_shake_data', 'x_shake_pos', 'y_shake_pos',
                                      'x_up_shake_data', 'y_up_shake_data', 'x_up_shake_pos', 'y_up_shake_pos'])
    grade_df = pd.DataFrame(columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                                     'rapid_time', 'grade_rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    r_i = 0
    g_i = 0
    for report in shoot_reports:
        print(report.shoot_date + " " + report.start_time)

        shoot_grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
        rapid_time = shoot_grades[4].rapid_time
        stage = 8
        if float(rapid_time) < 1:
            print(shoot_grades[3].rapid_time)
            if float(shoot_grades[3].rapid_time) < 4:
                stage = 4
            elif float(shoot_grades[3].rapid_time) < 6:
                stage = 6
            elif float(shoot_grades[3].rapid_time) < 8:
                stage = 8
            shoot_grades[4].rapid_time = stage + float(rapid_time)
        last_rapid = 0
        is_grade_not_zero = True
        for grade in shoot_grades:
            if int(grade.grade) == 0:
                is_grade_not_zero = False
                break
            print(grade.grade_detail_time)
            rapid_time = float(grade.rapid_time)
            if rapid_time < 1:
                rapid_time = int(report.remark) + rapid_time
            grade_rapid_time = rapid_time - last_rapid
            grade_df.loc[g_i] = [grade.report_id, grade.grade_date, grade.grade_time, grade.grade_detail_time,
                                 float(grade.grade), float(grade.rapid_time), grade_rapid_time, float(grade.x_pos),
                                 float(grade.y_pos), int(grade.heart_rate)]
            last_rapid = rapid_time
            g_i += 1
        if is_grade_not_zero:
            report_df.loc[r_i] = [report.id, report.shoot_date, report.shoot_time, report.start_time, report.end_time,
                                  float(report.total_grade), int(report.remark), report.x_shake_data,
                                  report.y_shake_data,
                                  report.x_shake_pos, report.y_shake_pos, report.x_up_shake_data,
                                  report.y_up_shake_data,
                                  report.x_up_shake_pos, report.y_up_shake_pos]
            r_i += 1
        else:
            print("grade zero")
        print()
    report_df.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/report_info.xlsx")
    grade_df.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_info.xlsx")


def save_first_shoot_info():
    shoot_reports = shoot_report.objects.all()
    print(len(shoot_reports))
    grade_first_shoot_df = pd.DataFrame(columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                                                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    g_i = 0
    for report in shoot_reports:
        print(report.shoot_date + " " + report.start_time)
        shoot_grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
        grade = shoot_grades[0]
        grade_first_shoot_df.loc[g_i] = [grade.report_id, grade.grade_date, grade.grade_time,
                                         grade.grade_detail_time,
                                         float(grade.grade), float(grade.rapid_time),
                                         float(grade.x_pos),
                                         float(grade.y_pos), int(grade.heart_rate)]
        g_i += 1

    grade_first_shoot_df.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info.xlsx")


def save_first_shoot_info_by_stage():
    shoot_reports = shoot_report.objects.all()
    print(len(shoot_reports))
    grade_first_shoot_df_4 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    grade_first_shoot_df_6 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    grade_first_shoot_df_8 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    g_i_4 = 0
    g_i_6 = 0
    g_i_8 = 0
    for report in shoot_reports:
        print(report.shoot_date + " " + report.start_time)
        shoot_grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
        grade = shoot_grades[0]
        stage = int(report.remark)
        if stage == 4:
            grade_first_shoot_df_4.loc[g_i_4] = [grade.report_id, grade.grade_date, grade.grade_time,
                                                 grade.grade_detail_time,
                                                 float(grade.grade), float(grade.rapid_time),
                                                 float(grade.x_pos),
                                                 float(grade.y_pos), int(grade.heart_rate)]
            g_i_4 += 1
        if stage == 6:
            grade_first_shoot_df_6.loc[g_i_6] = [grade.report_id, grade.grade_date, grade.grade_time,
                                                 grade.grade_detail_time,
                                                 float(grade.grade), float(grade.rapid_time),
                                                 float(grade.x_pos),
                                                 float(grade.y_pos), int(grade.heart_rate)]
            g_i_6 += 1
        if stage == 8:
            grade_first_shoot_df_8.loc[g_i_8] = [grade.report_id, grade.grade_date, grade.grade_time,
                                                 grade.grade_detail_time,
                                                 float(grade.grade), float(grade.rapid_time),
                                                 float(grade.x_pos),
                                                 float(grade.y_pos), int(grade.heart_rate)]
            g_i_8 += 1

    grade_first_shoot_df_4.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_4.xlsx")
    grade_first_shoot_df_6.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_6.xlsx")
    grade_first_shoot_df_8.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_8.xlsx")


def save_first_shoot_info_by_stage_with_stability():
    shoot_reports = shoot_report.objects.all()
    print(len(shoot_reports))
    grade_first_shoot_df_4 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate', 'x_average', 'y_stability'])
    grade_first_shoot_df_6 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate', 'x_average', 'y_stability'])
    grade_first_shoot_df_8 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate', 'x_average', 'y_stability'])

    grade_four_shoot_df_4 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate', 'rapid_diff', 'x_average', 'y_stability', 'move_speed'])
    grade_four_shoot_df_6 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate', 'rapid_diff', 'x_average', 'y_stability', 'move_speed'])
    grade_four_shoot_df_8 = pd.DataFrame(
        columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                 'rapid_time', 'x_pos', 'y_pos', 'heart_rate', 'rapid_diff', 'x_average', 'y_stability', 'move_speed'])
    g_i_4 = 0
    g_i_6 = 0
    g_i_8 = 0

    g_i_f_4 = 0
    g_i_f_6 = 0
    g_i_f_8 = 0
    for report in shoot_reports:
        print(report.shoot_date + " " + report.start_time)
        stage = int(report.remark)
        # print(report.y_shake_pos)
        # print(report.x_up_shake_data)
        y_data_pos = report.y_shake_pos.split(",")
        x_up_data_pos = report.x_up_shake_pos.split(",")
        y_up_data_pos = report.y_up_shake_pos.split(",")

        y_up_shake_data = shootlib.process_shake_pos_info(y_up_data_pos)
        y_shake_data = shootlib.process_shake_pos_info(y_data_pos)
        x_up_shake_data = shootlib.process_shake_pos_info(x_up_data_pos)

        y_up_data = y_up_shake_data.split(",")
        y_data = y_shake_data.split(",")
        x_up_data = x_up_shake_data.split(",")
        y_data = shootlib.get_int_data(y_data, is_negative=True)
        x_up_data = shootlib.get_int_data(x_up_data)
        y_up_data = shootlib.get_int_data(y_up_data)

        y_data, num = shootlib.cut_shake_data(y_data)
        x_up_data = x_up_data[num:]
        y_up_data = y_up_data[num:]

        if stage == 4:
            pos_num = 8
        elif stage == 6:
            pos_num = 10
        else:
            pos_num = 15
        after_shoot = 1

        nums, y_shoot_array = shootlib.get_shoot_point(y_data)
        # up_nums, x_shoot_array = shootlib.get_shoot_point(y_up_data, limit=5)
        y_data_plus = shootlib.shake_data_process(y_data)
        x_up_data_plus = shootlib.shake_data_process(x_up_data)
        y_shoot_pos, y_pos_array = shootlib.shake_get_plus_shoot_point(y_data_plus, nums, pos_num=pos_num,
                                                                       after_shoot=after_shoot)
        x_shoot_pos, x_pos_array = shootlib.shake_get_plus_shoot_point(x_up_data_plus, nums, pos_num=pos_num,
                                                                       after_shoot=after_shoot)
        if len(nums) == 5:
            # print(x_pos_array)
            x_average_array = shootlib.shake_get_average_x_shoot_array(x_pos_array, after_shoot)
            y_stability_array = shootlib.shake_get_stability_shoot_array(y_pos_array, after_shoot)
            # print(x_average_array)
            # print(y_stability_array)
            shoot_grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
            first_grade = shoot_grades[0]
            if stage == 4:
                grade_first_shoot_df_4.loc[g_i_4] = [first_grade.report_id, first_grade.grade_date,
                                                     first_grade.grade_time,
                                                     first_grade.grade_detail_time,
                                                     float(first_grade.grade), float(first_grade.rapid_time),
                                                     float(first_grade.x_pos),
                                                     float(first_grade.y_pos), int(first_grade.heart_rate),
                                                     x_average_array[0], y_stability_array[0]]
                g_i_4 += 1
            if stage == 6:
                grade_first_shoot_df_6.loc[g_i_6] = [first_grade.report_id, first_grade.grade_date,
                                                     first_grade.grade_time,
                                                     first_grade.grade_detail_time,
                                                     float(first_grade.grade), float(first_grade.rapid_time),
                                                     float(first_grade.x_pos),
                                                     float(first_grade.y_pos), int(first_grade.heart_rate),
                                                     x_average_array[0], y_stability_array[0]]
                g_i_6 += 1
            if stage == 8:
                grade_first_shoot_df_8.loc[g_i_8] = [first_grade.report_id, first_grade.grade_date,
                                                     first_grade.grade_time,
                                                     first_grade.grade_detail_time,
                                                     float(first_grade.grade), float(first_grade.rapid_time),
                                                     float(first_grade.x_pos),
                                                     float(first_grade.y_pos), int(first_grade.heart_rate),
                                                     x_average_array[0], y_stability_array[0]]
                g_i_8 += 1
            last_x_pos = float(first_grade.x_pos)
            last_rapid_time = float(first_grade.rapid_time)
            for i in range(1, len(shoot_grades)):
                grade = shoot_grades[i]
                diff_pos = (last_x_pos - float(grade.x_pos) + i * 750)
                diff_rapid = float(grade.rapid_time) - last_rapid_time
                if i == 4 and float(grade.rapid_time) < 1:
                    diff_rapid = float(grade.rapid_time) + stage - last_rapid_time
                if diff_rapid < 0:
                    print(i)
                    print("diff_rapid:" + str(diff_rapid))

                move_speed = round(diff_pos / diff_rapid, 2)
                last_x_pos = float(grade.x_pos)
                last_rapid_time = float(grade.rapid_time)
                if stage == 4:
                    grade_four_shoot_df_4.loc[g_i_f_4] = [grade.report_id, grade.grade_date, grade.grade_time,
                                                          grade.grade_detail_time,
                                                          float(grade.grade), float(grade.rapid_time),
                                                          float(grade.x_pos),
                                                          float(grade.y_pos), int(grade.heart_rate), diff_rapid,
                                                          x_average_array[i], y_stability_array[i], move_speed]
                    g_i_f_4 += 1
                if stage == 6:
                    grade_four_shoot_df_6.loc[g_i_f_6] = [grade.report_id, grade.grade_date, grade.grade_time,
                                                          grade.grade_detail_time,
                                                          float(grade.grade), float(grade.rapid_time),
                                                          float(grade.x_pos),
                                                          float(grade.y_pos), int(grade.heart_rate), diff_rapid,
                                                          x_average_array[i], y_stability_array[i], move_speed]
                    g_i_f_6 += 1
                if stage == 8:
                    grade_four_shoot_df_8.loc[g_i_f_8] = [grade.report_id, grade.grade_date, grade.grade_time,
                                                          grade.grade_detail_time,
                                                          float(grade.grade), float(grade.rapid_time),
                                                          float(grade.x_pos),
                                                          float(grade.y_pos), int(grade.heart_rate), diff_rapid,
                                                          x_average_array[i], y_stability_array[i], move_speed]
                    g_i_f_8 += 1

        else:
            print("data not find five shoot")

    grade_first_shoot_df_4.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_4_with_feature.xlsx")
    grade_first_shoot_df_6.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_6_with_feature.xlsx")
    grade_first_shoot_df_8.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_8_with_feature.xlsx")

    grade_four_shoot_df_4.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_four_shoot_info_4_with_feature.xlsx")
    grade_four_shoot_df_6.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_four_shoot_info_6_with_feature.xlsx")
    grade_four_shoot_df_8.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_four_shoot_info_8_with_feature.xlsx")


def save_report_by_stage():
    shoot_reports = shoot_report.objects.all()
    print(len(shoot_reports))
    report_df_4 = pd.DataFrame(columns=['id', 'shoot_date', 'shoot_time', 'start_time', 'end_time', 'total_grade',
                                        'stage', 'x_shake_data', 'y_shake_data', 'x_shake_pos', 'y_shake_pos',
                                        'x_up_shake_data', 'y_up_shake_data', 'x_up_shake_pos', 'y_up_shake_pos'])
    report_df_6 = pd.DataFrame(columns=['id', 'shoot_date', 'shoot_time', 'start_time', 'end_time', 'total_grade',
                                        'stage', 'x_shake_data', 'y_shake_data', 'x_shake_pos', 'y_shake_pos',
                                        'x_up_shake_data', 'y_up_shake_data', 'x_up_shake_pos', 'y_up_shake_pos'])
    report_df_8 = pd.DataFrame(columns=['id', 'shoot_date', 'shoot_time', 'start_time', 'end_time', 'total_grade',
                                        'stage', 'x_shake_data', 'y_shake_data', 'x_shake_pos', 'y_shake_pos',
                                        'x_up_shake_data', 'y_up_shake_data', 'x_up_shake_pos', 'y_up_shake_pos'])
    grade_df_4 = pd.DataFrame(columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                                       'rapid_time', 'grade_rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    grade_df_6 = pd.DataFrame(columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                                       'rapid_time', 'grade_rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    grade_df_8 = pd.DataFrame(columns=['report_id', 'grade_date', 'grade_time', 'grade_detail_time', 'grade',
                                       'rapid_time', 'grade_rapid_time', 'x_pos', 'y_pos', 'heart_rate'])
    r_i_4 = 0
    g_i_6 = 0
    r_i_8 = 0
    g_i_4 = 0
    r_i_6 = 0
    g_i_8 = 0
    for report in shoot_reports:
        print(report.shoot_date + " " + report.start_time)

        shoot_grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
        rapid_time = shoot_grades[4].rapid_time
        stage = int(report.remark)
        if float(rapid_time) < 1:
            shoot_grades[4].rapid_time = stage + float(rapid_time)
        last_rapid = 0
        is_grade_not_zero = True
        for grade in shoot_grades:
            if int(grade.grade) == 0:
                is_grade_not_zero = False
                break
            print(grade.grade_detail_time)
            rapid_time = float(grade.rapid_time)
            if rapid_time < 1:
                rapid_time = int(report.remark) + rapid_time
            grade_rapid_time = rapid_time - last_rapid
            if stage == 4:
                grade_df_4.loc[g_i_4] = [grade.report_id, grade.grade_date, grade.grade_time, grade.grade_detail_time,
                                         float(grade.grade), float(grade.rapid_time), grade_rapid_time,
                                         float(grade.x_pos),
                                         float(grade.y_pos), int(grade.heart_rate)]
                g_i_4 += 1
            elif stage == 6:
                grade_df_6.loc[g_i_6] = [grade.report_id, grade.grade_date, grade.grade_time, grade.grade_detail_time,
                                         float(grade.grade), float(grade.rapid_time), grade_rapid_time,
                                         float(grade.x_pos),
                                         float(grade.y_pos), int(grade.heart_rate)]
                g_i_6 += 1
            else:
                grade_df_6.loc[g_i_8] = [grade.report_id, grade.grade_date, grade.grade_time, grade.grade_detail_time,
                                         float(grade.grade), float(grade.rapid_time), grade_rapid_time,
                                         float(grade.x_pos),
                                         float(grade.y_pos), int(grade.heart_rate)]
                g_i_8 += 1

            last_rapid = rapid_time
        if is_grade_not_zero:
            if stage == 4:
                report_df_4.loc[r_i_4] = [report.id, report.shoot_date, report.shoot_time, report.start_time,
                                          report.end_time,
                                          float(report.total_grade), int(report.remark), report.x_shake_data,
                                          report.y_shake_data,
                                          report.x_shake_pos, report.y_shake_pos, report.x_up_shake_data,
                                          report.y_up_shake_data,
                                          report.x_up_shake_pos, report.y_up_shake_pos]
                r_i_4 += 1
            elif stage == 6:
                report_df_6.loc[r_i_6] = [report.id, report.shoot_date, report.shoot_time, report.start_time,
                                          report.end_time,
                                          float(report.total_grade), int(report.remark), report.x_shake_data,
                                          report.y_shake_data,
                                          report.x_shake_pos, report.y_shake_pos, report.x_up_shake_data,
                                          report.y_up_shake_data,
                                          report.x_up_shake_pos, report.y_up_shake_pos]
                r_i_6 += 1
            else:
                report_df_8.loc[r_i_8] = [report.id, report.shoot_date, report.shoot_time, report.start_time,
                                          report.end_time,
                                          float(report.total_grade), int(report.remark), report.x_shake_data,
                                          report.y_shake_data,
                                          report.x_shake_pos, report.y_shake_pos, report.x_up_shake_data,
                                          report.y_up_shake_data,
                                          report.x_up_shake_pos, report.y_up_shake_pos]
                r_i_8 += 1
        else:
            print("grade zero")
        print()
    report_df_4.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/report_info_4.xlsx")
    grade_df_4.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_info_4.xlsx")
    report_df_6.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/report_info_6.xlsx")
    grade_df_6.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_info_6.xlsx")
    report_df_8.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/report_info_8.xlsx")
    grade_df_8.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_info_8.xlsx")


def save_grade_info():
    shoot_grades = shoot_grade.objects.all()
    print(len(shoot_grades))
    for grade in shoot_grades:
        if 's' in grade.rapid_time:
            print(grade.grade_detail_time)
            print(grade.rapid_time)
            print()


if __name__ == "__main__":
    print("shoot")
    # test()
    # get_shoot_info()
    # x1, y1 = 31.33, 12.82
    # x2, y2 = 35.52, -7.48
    # x3, y3 = 2.96, 37.16
    # x4, y4 = - 32.49, 2.67
    # x5, y5 = - 26.68, -29.15
    # xs = [x1, x2, x3, x4, x5]
    # ys = [y1, y2, y3, y4, y5]
    # print(cart_to_polar(x1, y1))

    # xd, yd = polar_to_cart(0, 0, 50)
    # for x, y in zip(xd, yd):
    #     print(str(x) + " " + str(y))

    # update_shoot_report()
    # update_shoot_grade()

    # update_shake_time()
    # update_shake_data()

    # update_heart_time()
    # update_heart_data()

    # update_all_info()
    # update_grade_heart_info()
    # update_report_shake_info()

    # process_shake_data()
    # process_shake_time_data()

    # update_data("A")
    save_first_shoot_info_by_stage_with_stability()
