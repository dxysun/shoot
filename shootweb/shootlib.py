# -*- coding:utf-8 -*- 
import sys
import os
import datetime
import django
import time
import math
from scipy.interpolate import interp1d
from scipy import optimize
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


def update_data_bak(user_name):
    shoot_reports = shoot_report.objects.filter(is_process=0).filter(user_name=user_name)
    if len(shoot_reports) > 0:
        for report in shoot_reports:
            report_time = time_to_string(string_to_time(report.shoot_time) + datetime.timedelta(seconds=2))
            shake_times = record_shake_time.objects.filter(start_time__lte=report_time).filter(
                end_time__gte=report_time)
            if len(shake_times) == 1:
                print('find beside:' + report.shoot_time)
                shake = shake_times[0]
                report.x_shake_data = shake.shake_x_data
                report.y_shake_data = shake.shake_y_data
                report.x_up_shake_data_real = shake.shake_x_detail_data
                report.y_up_shake_data_real = shake.shake_y_detail_data
                report.is_process = 1
                shake.is_process = 1
                shake.save()
                report.save()
            else:
                print('not find beside ' + report.shoot_time)
            up_shake_times = record_up_shake_time.objects.filter(start_time__lte=report_time).filter(
                end_time__gte=report_time)
            if len(up_shake_times) == 1:
                print('find up:' + report.shoot_time)
                shake = up_shake_times[0]
                report.x_up_shake_data = shake.shake_x_data
                report.y_up_shake_data = shake.shake_y_data
                report.x_up_shake_data_real = shake.shake_x_detail_data
                report.y_up_shake_data_real = shake.shake_y_detail_data
                report.is_process = 1
                shake.is_process = 1
                shake.save()
                report.save()
            else:
                print('not find beside ' + report.shoot_time)
            grades = shoot_grade.objects.filter(report_id=report.id)
            for grade in grades:
                heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
                if len(heart_times) >= 1:
                    heart_time = heart_times[0]
                    grade.heart_rate = heart_time.average_rate
                else:
                    print('no data')
                    grade.heart_rate = 0
                grade.save()


def update_data(user_name):
    shake_datas = shake_all_info.objects.filter(user_name=user_name)
    for data in shake_datas:
        record_time = data.record_time
        report_times = shoot_report.objects.filter(shoot_date=data.record_date).filter(
            start_time__lte=record_time).filter(end_time__gte=record_time)
        if len(report_times) > 0:
            if string_to_time(data.end_time) - string_to_time(data.start_time) <= datetime.timedelta(seconds=2):
                print("delete " + data.record_time)
                data.delete()
        else:
            print(data.record_time + "  not find data")
            data.delete()

    shoot_reports = shoot_report.objects.filter(is_process=0).filter(user_name=user_name)
    if len(shoot_reports) > 0:
        for report in shoot_reports:
            report_time = time_to_string_mill(string_to_time_mill(report.shoot_time) + datetime.timedelta(seconds=2))
            shake_times = shake_all_info.objects.filter(start_time__lte=report_time).filter(
                end_time__gte=report_time)
            if len(shake_times) == 1:
                print('find beside:' + report.shoot_time)
                shake = shake_times[0]
                report.x_shake_data = shake.beside_x_data
                report.y_shake_data = shake.beside_y_data
                report.x_shake_pos = shake.beside_x_pos
                report.y_shake_pos = shake.beside_y_pos
                report.x_up_shake_data = shake.up_x_data
                report.y_up_shake_data = shake.up_y_data
                report.x_up_shake_pos = shake.up_x_pos
                report.y_up_shake_pos = shake.up_y_pos
                report.is_process = 1
                shake.is_process = 1
                shake.save()
                report.save()
            else:
                print('not find beside ' + report.shoot_time)
            grades = shoot_grade.objects.filter(report_id=report.id)
            for grade in grades:
                heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
                if len(heart_times) >= 1:
                    heart_time = heart_times[0]
                    grade.heart_rate = heart_time.average_rate
                else:
                    print('no data')
                    grade.heart_rate = 0
                grade.save()


def insert(x_data, y_data):
    x = []
    for i in range(1, len(x_data) * 5, 5):
        x.append(i)
    x = np.array(x)
    x_f3 = interp1d(x, x_data, kind='cubic')
    y_f3 = interp1d(x, y_data, kind='cubic')
    x_data_new = []
    y_data_new = []
    for i in range(x.min(), x.max() + 1):
        x_data_new.append(str(round(float(x_f3(i).tolist()), 2)))
        y_data_new.append(str(round(float(y_f3(i).tolist()), 2)))
    return x_data_new, y_data_new


def get_int_data(list_data, is_negative=False):
    temp_data = []
    for data in list_data:
        d = int(data)
        if is_negative:
            d *= -1
        temp_data.append(d)
    return temp_data


def shake_data_process(data_shake, nums=None, is_insert=False):
    plus_num = 0
    data_ori = ""
    data_plus = ""
    data_plus_array = []
    pos_array = []
    pos = ""
    j = 0
    n = 20
    if is_insert:
        n = 80
    for i in range(0, len(data_shake)):
        data_ori += str(data_shake[i]) + ","
        data = float(data_shake[i])
        plus_num += data
        plus_num = round(plus_num, 2)
        data_plus_array.append(plus_num)
        data_plus += str(plus_num) + ","
    if nums is None:
        return data_ori, data_plus
    else:
        for i in range(0, len(data_plus_array)):
            plus_num = data_plus_array[i]
            if j < len(nums) and i == nums[j]:
                pos_array.append(data_plus_array[i - n:i])
                pos += str(plus_num) + ","
                j += 1
        return data_ori, data_plus, pos[:-1], pos_array


def cut_shake_data(y_shake_data):
    count_smooth = 0
    rank = -1
    for data in y_shake_data:
        rank += 1
        if count_smooth < 10 < int(data):
            count_smooth = 0
            continue
        if abs(data) < 10:
            # print(data)
            count_smooth += 1
        if count_smooth == 10:
            break
    # print(rank)
    return y_shake_data[rank - 9:], rank - 9


def process_grade_rapid_time(rapid_data):
    data = []
    for i in range(0, len(rapid_data)):
        if i == 0:
            data.append(float(rapid_data[i]))
        else:
            data.append(round(float(rapid_data[i]) - float(rapid_data[i - 1]), 2))
    return data


# def get_shoot_point(beside_y_data, up_x_data, rapid_data):
#     shoot_info = {}
#     r = 0
#     frames = 35
#     shoot_name = ['one', 'two', 'three', 'four', 'five']
#
#     for i in range(0, len(beside_y_data)):
#         x = up_x_data[i]
#         y = beside_y_data[i]
#         if y > 10:
#             if r == 0:
#                 shoot_info[shoot_name[r]] = []
#                 shoot_info[shoot_name[r]].append(up_x_data[:i])
#                 shoot_info[shoot_name[r]].append(beside_y_data[:i])
#             else:
#                 t = frames * rapid_data[r] - 5
#                 shoot_info[shoot_name[r]] = []
#                 shoot_info[shoot_name[r]].append(up_x_data[i - t:i])
#                 shoot_info[shoot_name[r]].append(beside_y_data[i - t:i])
#             r += 1
def get_shoot_point(beside_y_data, is_insert=False):
    nums = []
    is_smooth = False
    count_smooth = 0
    for i in range(0, len(beside_y_data)):
        y = beside_y_data[i]
        if y > 10:
            count_smooth = 0
        else:
            count_smooth += 1
            if count_smooth > 10:
                is_smooth = True
        if is_smooth and y >= 10:
            if beside_y_data[i - 1] > 5:
                if is_insert:
                    nums.append((i - 2) * 5)
                else:
                    nums.append(i - 2)
            else:
                if is_insert:
                    nums.append((i - 1) * 5)
                else:
                    nums.append(i - 1)
            count_smooth = 0
            is_smooth = False
    return nums


def fun(x, a, b, c):
    return a * x * x + b * x + c


def get_shoot_info(y_sum_data):
    start = 0
    for end in range(10, len(y_sum_data)):
        y = y_sum_data[start:end]
        x = []
        for i in range(start, end):
            x.append(i)
        popt, pcov = optimize.curve_fit(fun, x, y)
        a = popt[0]
        b = popt[1]
        mid = - (b / (2 * a))
        if start < mid < end:
            print(start)
            print(end)
            print()
        start += 1


if __name__ == "__main__":
    print("shoot")
    # print(3 ** 2)
    y_data = [-17.0, 21.0, 52.0, 75.0, 95.0, 110.0, 125.0, 136.0, 144.0, 152.0, 160.0, 168.0, 172.0, 175.0, 179.0,
              182.0, 187.0, 189.0, 193.0, 197.0, 201.0, 205.0, 207.0, 209.0, 213.0, 215.0, 216.0, 216.0, 217.0, 219.0,
              221.0, 222.0, 223.0, 225.0, 225.0, 227.0, 228.0, 229.0, 230.0, 230.0, 238.0, 255.0, 254.0, 259.0, 264.0,
              260.0, 254.0, 248.0, 246.0, 243.0, 241.0, 240.0, 239.0, 237.0, 235.0, 232.0, 230.0, 228.0, 227.0, 227.0,
              228.0, 228.0, 228.0, 228.0, 228.0, 229.0, 229.0, 229.0, 229.0, 229.0, 229.0, 229.0, 230.0, 231.0, 234.0,
              234.0, 236.0, 261.0, 263.0, 265.0, 268.0, 271.0, 260.0, 253.0, 248.0, 244.0, 242.0, 242.0, 242.0, 243.0,
              245.0, 245.0, 245.0, 247.0, 248.0, 248.0, 247.0, 247.0, 246.0, 246.0, 246.0, 245.0, 244.0, 244.0, 244.0,
              243.0, 242.0, 243.0, 243.0, 244.0, 244.0, 247.0, 266.0, 265.0, 269.0, 268.0, 265.0, 260.0, 256.0, 253.0,
              252.0, 250.0, 249.0, 248.0, 248.0, 248.0, 247.0, 245.0, 244.0, 242.0, 242.0, 241.0, 241.0, 240.0, 240.0,
              241.0, 240.0, 241.0, 242.0, 243.0, 243.0, 243.0, 244.0, 245.0, 246.0, 268.0, 269.0, 275.0, 277.0, 275.0,
              269.0, 264.0, 258.0, 254.0, 253.0, 251.0, 249.0, 248.0, 247.0, 246.0, 242.0, 241.0, 240.0, 240.0, 240.0,
              240.0, 240.0, 240.0, 240.0, 241.0, 242.0, 241.0, 241.0, 241.0, 242.0, 242.0, 242.0, 243.0, 244.0, 245.0,
              267.0, 267.0, 272.0, 275.0, 276.0, 275.0, 275.0, 275.0, 272.0, 269.0, 266.0, 266.0, 266.0, 265.0, 264.0,
              262.0, 260.0, 258.0, 248.0, 240.0, 226.0, 212.0, 198.0, 184.0, 170.0, 156.0, 142.0, 128.0, 114.0, 100.0]
    get_shoot_info(y_data)
