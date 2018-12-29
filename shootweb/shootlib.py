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
import random
import matplotlib.pyplot as plt

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


def cart_to_polar_1(x, y):
    z = pow(x, 2) + pow(y, 2)
    r = math.sqrt(z)
    angle = math.atan2(y, x) * 180 / math.pi
    if angle < 0:
        angle = 360 + angle
    r = round(r, 2)
    angle = round(angle, 2)
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


def update_data(user_name):
    shake_datas = shake_all_info.objects.filter(is_process=0).filter(user_name=user_name)
    for data in shake_datas:
        record_time = data.record_time
        # record_time = time_to_string_mill(string_to_time(record_time) - datetime.timedelta(seconds=7))
        report_times = shoot_report.objects.filter(shoot_date=data.record_date).filter(
            start_time__lte=record_time).filter(end_time__gte=record_time)
        if len(report_times) > 0:
            # print(len(report_times))
            print(data.record_time + " shake  find report data " + report_times[0].start_time)
            if string_to_time(data.end_time) - string_to_time(data.start_time) <= datetime.timedelta(seconds=2):
                print("delete " + data.record_time)
                data.delete()
        else:
            print(data.record_time + " shake  not find report data")
            data.is_process = 1
            data.delete()

    shoot_reports = shoot_report.objects.filter(is_process=0).filter(user_name=user_name)
    if len(shoot_reports) > 0:
        for report in shoot_reports:
            # report_time = time_to_string_mill(string_to_time_mill(report.shoot_time) + datetime.timedelta(seconds=10))
            # print(report_time)
            report_time = time_to_string_mill(string_to_time_mill(report.shoot_time) + datetime.timedelta(seconds=2))
            shake_times = shake_all_info.objects.filter(record_date=report.shoot_date).filter(
                start_time__lte=report_time).filter(end_time__gte=report_time)
            if len(shake_times) == 1:
                print('find shake:' + report.shoot_time)
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
                print('not find shake ' + report.shoot_time)
            grades = shoot_grade.objects.filter(report_id=report.id)
            for grade in grades:
                heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
                if len(heart_times) >= 1:
                    print('find heart data')
                    heart_time = heart_times[0]
                    grade.heart_rate = heart_time.average_rate
                else:
                    print('no heart data')
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


def shake_data_process(data_shake, is_negative=False):
    plus_num = 0
    data_plus_array = []
    for i in range(0, len(data_shake)):
        data = float(data_shake[i])
        if is_negative:
            data *= -1
        plus_num += data
        plus_num = round(plus_num, 2)
        data_plus_array.append(plus_num)
    return data_plus_array


def shake_get_plus_shoot_point(data_plus_array, nums, is_insert=False):
    pos_array = []
    pos = []
    j = 0
    n = 10
    m = 0
    if is_insert:
        n *= 5
        m = 5
    for i in range(0, len(data_plus_array)):
        plus_num = data_plus_array[i]
        if j < len(nums) and i == nums[j]:
            if i - n > 0:
                pos_array.append(data_plus_array[i - n:i + m])
            else:
                pos_array.append(data_plus_array[0:i + m])
            pos.append(plus_num)
            j += 1
    return pos, pos_array


def cut_shake_data(y_shake_data):
    count_smooth = 0
    rank = -1
    for data in y_shake_data:
        rank += 1
        if count_smooth < 5 and 10 < int(data):
            count_smooth = 0
            continue
        if abs(data) < 10:
            # print(data)
            count_smooth += 1
        if count_smooth == 5:
            break
    # print(rank)
    return y_shake_data[rank - 4:], rank - 4


def process_grade_rapid_time(rapid_data):
    data = []
    for i in range(0, len(rapid_data)):
        if i == 0:
            data.append(float(rapid_data[i]))
        else:
            data.append(round(float(rapid_data[i]) - float(rapid_data[i - 1]), 2))
    return data


def get_shoot_point(beside_y_data, is_insert=False, limit=10):
    nums = []
    is_smooth = False
    count_smooth = 0
    for i in range(0, len(beside_y_data)):
        y = beside_y_data[i]
        if is_smooth and y > limit:
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
            continue
        if len(nums) == 5:
            break
        if y > limit:
            count_smooth = 0
        else:
            count_smooth += 1
            if count_smooth >= 5:
                is_smooth = True
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


def process_shake_pos_info(beside_x_pos, beside_y_pos, up_x_pos, up_y_pos):
    beside_x_pos = beside_x_pos.split(",")
    beside_y_pos = beside_y_pos.split(",")
    up_x_pos = up_x_pos.split(",")
    up_y_pos = up_y_pos.split(",")
    beside_x_data = "0,"
    beside_y_data = "0,"
    up_x_data = "0,"
    up_y_data = "0,"
    for i in range(1, len(beside_x_pos)):
        d_x = int(beside_x_pos[i]) - int(beside_x_pos[i - 1])
        d_y = int(beside_y_pos[i]) - int(beside_y_pos[i - 1])
        beside_x_data += str(d_x) + ","
        beside_y_data += str(d_y) + ","
    beside_x_data = beside_x_data[:-1]
    beside_y_data = beside_y_data[:-1]

    for i in range(1, len(up_x_pos)):
        d_x = int(up_x_pos[i]) - int(up_x_pos[i - 1])
        d_y = int(up_y_pos[i]) - int(up_y_pos[i - 1])
        up_x_data += str(d_x) + ","
        up_y_data += str(d_y) + ","
    up_x_data = up_x_data[:-1]
    up_y_data = up_y_data[:-1]
    return beside_x_data, beside_y_data, up_x_data, up_y_data


def array_to_str(data):
    data_str = ""
    for i in range(0, len(data)):
        data_str += str(data[i]) + ","
    return data_str[:-1]


def get_up_shoot_limit(x_up_shoot_pos, x_pos, grades):
    up_x_10_pos = []
    up_shake_rate = None
    if len(x_up_shoot_pos) == 5:
        if x_pos[0] > 0:
            left = 50 - x_pos[0]
        else:
            left = 50 + x_pos[0]
        if x_pos[4] > 0:
            right = 50 + x_pos[4]
        else:
            right = 50 - x_pos[4]
        pos_cha = 3100 - (left + right)
        up_x_cha = (x_up_shoot_pos[4] - x_up_shoot_pos[0]) * -1
        up_shake_rate = pos_cha / up_x_cha
        # print(up_shake_rate)
        for i in range(0, 5):
            if grades[i] == 10:
                if x_pos[i] > 0:
                    cha10_r = 50 - abs(x_pos[i])
                    cha10_r = cha10_r / up_shake_rate
                    cha10_r = x_up_shoot_pos[i] + cha10_r
                    cha10_l = 50 + abs(x_pos[i])
                    cha10_l = cha10_l / up_shake_rate
                    cha10_l = x_up_shoot_pos[i] - cha10_l
                else:
                    cha10_r = 50 + abs(x_pos[i])
                    cha10_r = cha10_r / up_shake_rate
                    cha10_r = x_up_shoot_pos[i] + cha10_r
                    cha10_l = 50 - abs(x_pos[i])
                    cha10_l = cha10_l / up_shake_rate
                    cha10_l = x_up_shoot_pos[i] - cha10_l
                up_x_10_pos.append(round(cha10_r, 2))
                up_x_10_pos.append(round(cha10_l, 2))
            if grades[i] == 9 or grades[i] == 8:
                if x_pos[i] > 0:
                    cha10_r = abs(x_pos[i]) - 50
                    cha10_r = cha10_r / up_shake_rate
                    cha10_r = x_up_shoot_pos[i] - cha10_r
                    cha10_l = abs(x_pos[i]) + 50
                    cha10_l = cha10_l / up_shake_rate
                    cha10_l = x_up_shoot_pos[i] - cha10_l
                else:
                    cha10_r = abs(x_pos[i]) + 50
                    cha10_r = cha10_r / up_shake_rate
                    cha10_r = x_up_shoot_pos[i] + cha10_r
                    cha10_l = abs(x_pos[i]) - 50
                    cha10_l = cha10_l / up_shake_rate
                    cha10_l = x_up_shoot_pos[i] + cha10_l
                up_x_10_pos.append(round(cha10_r, 2))
                up_x_10_pos.append(round(cha10_l, 2))
    return up_x_10_pos, up_shake_rate


def split_report(reports):
    temp_report = []
    all_report = []
    temp_report.append(reports[0])
    for i in range(1, len(reports)):
        # print(reports[i].start_time)
        if len(reports[i - 1].start_time) > 3:
            r1_time = string_to_time_mill(reports[i - 1].start_time)
            r2_time = string_to_time_mill(reports[i].start_time)
            # print(r1_time)
            # print(r2_time)
            if r2_time - r1_time > datetime.timedelta(minutes=5):
                all_report.append(temp_report)
                temp_report = []
            temp_report.append(reports[i])

    if len(temp_report) > 0:
        all_report.append(temp_report)
    return all_report


def get_grade_stability(x_pos, y_pos):
    res = 0
    for x, y in zip(x_pos, y_pos):
        res += math.sqrt(x * x + y * y)
    return round(res / len(x_pos), 2)


def process_pos_array(pos_array, shoot_pos, up_shake_rate, is_average=False, is_insert=False):
    y_pos_average_str = []
    y_pos_str = []
    last_num = None
    temp_sum = 0
    i = 5 - len(pos_array)
    shoot_point = []
    j = 1
    if is_insert:
        j = 6
    for pos_a in pos_array:
        temp = []
        for y_d in pos_a:
            if is_average:
                if last_num is not None:
                    cha = y_d - last_num
                    temp_sum += cha
                last_num = y_d
            d1 = round(y_d - pos_a[len(pos_a) - j], 2) + int(shoot_pos[i] / up_shake_rate)
            temp.append(d1)
        shoot_point.append(temp[len(pos_a) - j])
        i += 1
        if is_average:
            y_pos_average_str.append(round(temp_sum / (len(pos_a) - 1), 2))
        y_pos_str.append(temp)
    if is_average:
        return y_pos_str, shoot_point, y_pos_average_str
    else:
        return y_pos_str, shoot_point


def get_shoot_date(user_name):
    shoot_reports = shoot_report.objects.filter(user_name=user_name).values('shoot_date').distinct()
    shoot_dates = []
    for r in shoot_reports:
        shoot_dates.append(r['shoot_date'])
    return shoot_dates


def g_1(r, r_e=130):
    if r == 0:
        res = 0
    elif r == r_e:
        res = 1
    else:
        res = (r * r) / (r_e * r_e)
    return res


def g_2(a, a_e=360):
    if a == 0:
        res = 0
    elif a == a_e:
        res = 1
    else:
        res = a / a_e
    return res


def j_radius(radius):
    b = g_1(radius[0])
    n = len(radius)
    for k in range(1, len(radius) - 1):
        g_k = g_1(radius[k])
        g_k_1 = g_1(radius[k + 1])
        temp = g_k_1 - g_k - (k / n) * (k / n) * (1 / g_k_1 - 1 / g_k) - (2 * k / n) * math.log(g_k_1 / g_k)
        b += temp
    return 1 - math.sqrt(b)


def j_angle(angle):
    b = g_2(angle[0])
    n = len(angle)
    for k in range(1, len(angle) - 1):
        g_k = g_2(angle[k])
        g_k_1 = g_2(angle[k + 1])
        temp = g_k_1 - g_k - (k / n) * (k / n) * (1 / g_k_1 - 1 / g_k) - (2 * k / n) * math.log(g_k_1 / g_k)
        b += temp
    return 1 - math.sqrt(b)


def get_average_in_circle(x_pos, y_pos):
    r_pos = []
    a_pos = []
    for x, y in zip(x_pos, y_pos):
        r, angle = cart_to_polar_1(x, y)
        r_pos.append(r)
        a_pos.append(angle)
    j_r = j_radius(r_pos)
    j_a = j_angle(a_pos)
    return j_r * j_a


def get_random_circle(r, samples_num):
    r_pos = []
    a_pos = []
    t = np.random.random(size=samples_num) * 2 * np.pi
    x = np.cos(t) * r
    y = np.sin(t) * r
    i_set = np.arange(0, samples_num, 1)
    for i in i_set:
        len = np.sqrt(np.random.random())
        x[i] = x[i] * len
        y[i] = y[i] * len
        radius1, angle = cart_to_polar_1(x[i], y[i])
        r_pos.append(radius1)
        a_pos.append(angle)
    plt.figure(figsize=(10, 10.1), dpi=125)
    plt.plot(x, y, 'ro')
    _t = np.arange(0, 7, 0.1)
    _x = np.cos(_t) * r
    _y = np.sin(_t) * r
    plt.plot(_x, _y, 'g-')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Random Scatter')
    plt.grid(True)
    # plt.show()
    return r_pos, a_pos


if __name__ == "__main__":
    print("shoot")
    # r_pos_1, a_pos_1 = get_random_circle(130, 800)
    # print(get_average_in_circle(r_pos_1, a_pos_1))
    # plt.show()
