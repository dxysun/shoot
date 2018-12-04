# -*- coding:utf-8 -*- 
import sys
import os
import datetime
import django
import time
import math

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


# 把字符串转成datetime
def string_to_time(string):
    return datetime.datetime.strptime(string, "%H:%M:%S")


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


def update_shoot_report():
    shoot_reports = shoot_report.objects.all()
    for report in shoot_reports:
        print(report.shoot_date)
        # print(report.shoot_date[:-9])
        # report.shoot_time = report.shoot_date[-8:]
        # report.shoot_date = "2018-07-14"
        report.user_name = "A"
        report.save()


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
    grades = shoot_grade.objects.all()
    for grade in grades:
        if grade.heart_rate == 0:
            print(grade.grade_time)
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
    shoot_reports = shoot_report.objects.filter(is_process=0)
    for report in shoot_reports:
        report_time = time_to_string(string_to_time(report.shoot_time) + datetime.timedelta(seconds=4))
        shake_times = record_shake_time.objects.filter(start_time__lte=report_time).filter(end_time__gte=report_time)
        if len(shake_times) == 1:
            print('find ' + report.shoot_time)
            shake = shake_times[0]
            report.x_shake_data = shake.shake_x_data
            report.y_shake_data = shake.shake_y_data
            report.is_process = 1
            shake.is_process = 1
            shake.save()
            report.save()
        else:
            print('not find ' + report.shoot_time)


def update_data(user_name):
    shoot_reports = shoot_report.objects.filter(is_process=0).filter(user_name=user_name)
    if len(shoot_reports) > 0:
        for report in shoot_reports:
            report_time = time_to_string(string_to_time(report.shoot_time) + datetime.timedelta(seconds=3))
            shake_times = record_shake_time.objects.filter(start_time__lte=report_time).filter(
                end_time__gte=report_time)
            if len(shake_times) == 1:
                print('find ' + report.shoot_time)
                shake = shake_times[0]
                report.x_shake_data = shake.shake_x_data
                report.y_shake_data = shake.shake_y_data
                report.is_process = 1
                shake.is_process = 1
                shake.save()
                report.save()
            else:
                print('not find ' + report.shoot_time)
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

    # update_shoot_report()
    # update_shoot_grade()

    # update_shake_time()
    # update_shake_data()

    # update_heart_time()
    # update_heart_data()

    # update_all_info()
    # update_grade_heart_info()
    # update_report_shake_info()
