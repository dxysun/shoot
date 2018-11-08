# -*- coding:utf-8 -*-
import sys
import os
import datetime
import django

sys.path.append('../shoot')
os.chdir('../shoot')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot.settings")
django.setup()
from shootweb.models import *


def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)


# 把datetime转成字符串
def datetime_to_string(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# 把字符串转成datetime
def string_to_datetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


# 把datetime转成字符串
def time_to_string(dt):
    return dt.strftime("%H-%M-%S")


# 把字符串转成datetime
def string_to_time(string):
    return datetime.datetime.strptime(string, "%H-%M-%S")


def read_context_from_file(file_path, save_path):
    context = ""
    with open(file_path, 'r', encoding='ISO-8859-15') as file:
        data = file.readlines()  # 读取全部内容 ，并以列表方式返回
        for line in data:
            line = line.strip('\n')
            line = line.replace("ÿ", "")
            line = line.strip()
            if line[1:2] == "%":
                line = line[3:]
            line = line.strip()
            index = line.find(' ')
            if index > 0 and line[0:index].isdigit() and line[index:index + 1] == " ":
                line1 = line[0:index]
                line2 = line[index + 3:].strip()
                line = line1 + " " + line2
            a = line.split(" ")
            line = ""
            for b in a:
                if b != "":
                    line += b + " "
            context += line.strip() + "\n"
    with open(save_path, 'w') as file:
        file.write(context)


def write_shoot_grade_to_mysql(file_path):
    with open(file_path, 'r') as file:
        # data = file.readlines()  # 读取全部内容 ，并以列表方式返回
        context = {}
        data = file.readline()
        num = 0
        report = ''
        b = False
        t = 0
        while data:
            line = data.strip('\n')
            # print(line)
            if b and t <= 10:
                context[report].append(line)
                t += 1
                if t > 10:
                    b = False
                    t = 0
            if line == 'Shot Report' and not b:
                num += 1
                report = 'ShotReport' + str(num)
                context[report] = []
                b = True
                t = 1
            data = file.readline()
        last = 0
        hours = 10
        for key, value in context.items():
            print(key)
            i = 5
            start_time = ''
            end_time = ''
            report_data = shoot_report(shoot_date='2018-07-14', start_time=start_time, end_time=end_time)
            report_data.save()
            while i > 0:
                j = i * 2
                grade = value[j - 2]
                grade = grade.split(" ")
                rapid_time = value[j - 1]
                rapid_time = rapid_time[1:5]
                g = grade[1]
                if 'P' in g:
                    g = g[0:len(g) - 2]
                t = grade[2]
                x = grade[3]
                y = grade[4]
                if t == 'P':
                    t = grade[3]
                    x = grade[4]
                    y = grade[5]
                x = x[0:len(x) - 1]
                if j == 10:
                    start_time = t
                if j == 2:
                    end_time = t
                if last != 0:
                    n = int(t[0:2])
                    if n < last:
                        hours += 1
                last = int(start_time[0:2])
                hours_str = str(hours) + ':' + t[0:5]
                shoot_data = shoot_grade(report_id=report_data.id, grade_date='2018-07-14 ' + hours_str, grade_time=t,
                                         grade=g, rapid_time=rapid_time, x_pos=x, y_pos=y)
                shoot_data.save()
                i -= 1
            report_data.shoot_date = '2018-07-14 ' + str(hours) + ':' + start_time[0:5].replace('-', ':')
            report_data.start_time = start_time
            report_data.end_time = end_time
            report_data.save()


def read_heart_from_file(file_path, save_dir):
    del_file(save_dir)
    files = os.listdir(file_path)
    for heart_file in files:
        heart_file_path = file_path + "/" + heart_file
        record_time = heart_file[16:24]
        record_time = string_to_time(record_time)
        record_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
        # print(record_time)
        with open(heart_file_path, 'r') as file:
            # print(file.read())
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            records = {}
            temp = ""
            for line in data:
                line = line.strip()
                if '-' in line:
                    temp = line
                if records.get(temp) is None:
                    records[temp] = []
                else:
                    records[temp].append(line)
            context = ""
            for key, value in records.items():
                t1 = string_to_time(key)
                new_time = time_to_string(t1 - datetime.timedelta(minutes=1, seconds=27))
                context += new_time + " : "
                for rate in value:
                    context += rate + " "
                context += "\n"
            with open(save_dir + record_time + '.txt', 'w') as f:
                f.write(context)


def read_heart_from_file_second(file_path, save_dir):
    del_file(save_dir)
    files = os.listdir(file_path)
    for heart_file in files:
        heart_file_path = file_path + "/" + heart_file
        record_time = heart_file[16:24]
        record_time = string_to_time(record_time)
        record_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
        # print(record_time)
        with open(heart_file_path, 'r', encoding='gbk') as file:
            # print(file.read())
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            records = {}
            for line in data:
                line = line.strip()
                line = line.split("：")
                if records.get(line[0]) is None:
                    records[line[0]] = []
                records[line[0]].append(line[1])
            # print(records)
            context = ""
            for key, value in records.items():
                t1 = string_to_time(key)
                new_time = time_to_string(t1 - datetime.timedelta(minutes=1, seconds=27))
                context += new_time + " : "
                for rate in value:
                    context += rate + " "
                context += "\n"
            with open(save_dir + record_time + '.txt', 'w') as f:
                f.write(str(context))


def get_normal_str(s):
    s = s.strip()
    if int(s) < 10:
        s = "0" + s
    return s


def read_heart_from_file_third(file_path):
    files = os.listdir(file_path)
    for heart_file in files:
        heart_file_path = file_path + "/" + heart_file
        print(heart_file)
        print(heart_file[2:12])
        print(heart_file[13:21])
        with open(heart_file_path, 'r', encoding='gbk') as file:
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            for line in data:
                line = line.strip()
                print(line)
                if "END" in line:
                    break
                d1 = line.split("-")
                # print(d1)
                date = get_normal_str(d1[0]) + "-" + get_normal_str(d1[1]) + "-" + get_normal_str(d1[2])
                print(date)
                d2 = d1[3]
                d3 = d2.split(":")
                # print(d3)
                h_time = get_normal_str(d3[0]) + "-" + get_normal_str(d3[1]) + "-" + get_normal_str(d3[2])
                print(h_time)
                d4 = d3[3]
                d5 = d4.split("\t")
                print(d5[-1])


def read_camera_from_file(file_path, file_type, save_dir):
    del_file(save_dir)
    files = os.listdir(file_path)
    first = file_path.find('camera')
    after_file_path = file_path[first:first + 7]
    # if 'horizontal' in file_path or 'vertical' in file_path:
    #     after_file_path += 'beside'
    # print(after_file_path)
    for camera_file in files:
        camera_file_path = file_path + "/" + camera_file
        if file_type == 'up':
            record_time = camera_file[13:21]
        else:
            record_time = camera_file[18:26]
        record_time = string_to_time(record_time)
        record_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
        # print(record_time)
        with open(camera_file_path, 'r') as file:
            data = file.readlines()
            minute = record_time[3:5]
            second = float(record_time[6:])
            context = ""
            for line in data:
                line = line.strip()
                data = float(line)
                shake = str('%.02f' % data)
                second += 0.033
                line = shake + " " + minute + ":" + str('%.02f' % second).zfill(5)
                # print(line)
                context += line + "\n"
            with open(save_dir + record_time + '.txt', 'w') as f:
                f.write(context)


def read_camera_from_file_second(file_path, file_type, save_dir):
    del_file(save_dir)
    files = os.listdir(file_path)
    for camera_file in files:
        camera_file_path = file_path + "/" + camera_file
        if file_type == "up":
            record_time = camera_file[13:21]
        else:
            record_time = camera_file[18:26]
        record_time = string_to_time(record_time)
        record_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
        # print(record_time)
        with open(camera_file_path, 'r', encoding='gbk') as file:
            # print(file.read())
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            records = {}
            for line in data:
                line = line.strip()
                line = line.split("：")
                if records.get(line[0]) is None:
                    records[line[0]] = []
                records[line[0]].append(line[1])
            # print(records)
            context = ""
            for key, value in records.items():
                t1 = string_to_time(key)
                new_time = time_to_string(t1 - datetime.timedelta(minutes=1, seconds=27))
                context += new_time + " : " + str(len(value)) + " : "
                for shake in value:
                    shake = shake.split('.')
                    data = float(shake[0]) / 1000
                    context += str('%.03f' % data) + ","
                context += "\n"
            with open(save_dir + record_time + '.txt', 'w') as f:
                f.write(str(context))


def find_n_sub_str(src, sub, pos, start):
    index = src.find(sub, start)
    if index != -1 and pos > 0:
        return find_n_sub_str(src, sub, pos - 1, index + 1)
    return index


def read_camera_from_file_third(file_path):
    files = os.listdir(file_path)
    for camera_file in files:
        camera_file_path = file_path + "/" + camera_file
        print(camera_file)
        print(camera_file[2:12])
        print(camera_file[13:21])
        with open(camera_file_path, 'r', encoding='gbk') as file:
            # print(file.read())
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            for line in data:
                line = line.strip()
                print(line)
                if "END" in line:
                    break
                i = find_n_sub_str(line, "-", 2, 0)
                line1 = line[:i]
                line2 = line[i + 1:]
                d1 = line1.split("-")
                # print(d1)
                date = get_normal_str(d1[0]) + "-" + get_normal_str(d1[1]) + "-" + get_normal_str(d1[2])
                print(date)
                d2 = line2
                d3 = d2.split(":")
                # print(d3)
                h_time = get_normal_str(d3[0]) + "-" + get_normal_str(d3[1]) + "-" + get_normal_str(d3[2])
                print(h_time)
                d4 = d3[3]
                d5 = d4.split("\t")
                print(d5[-2])
                print(d5[-1])


def merge_x_y_to_file(x_files_path, y_files_path, merge_file_path):
    x_files = os.listdir(x_files_path)
    y_files = os.listdir(y_files_path)
    x_data = {}
    for x_file in x_files:
        x_file_path = x_files_path + "/" + x_file
        # print(x_file[0:8])
        with open(x_file_path, 'r') as file:
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            x_data[x_file[0:8]] = data

    for y_file in y_files:
        y_file_path = y_files_path + "/" + y_file
        print(y_file[0:8])
        with open(y_file_path, 'r') as file:
            y_pos = file.readlines()  # 读取全部内容 ，并以列表方式返回
            x_pos = x_data[y_file[0:8]]
            # print("x_pos:" + str(len(x_pos)))
            # print("y_pos:" + str(len(y_pos)))
            context = ""
            for i in range(0, len(y_pos)):
                pos_info = x_pos[i].strip() + "\n" + y_pos[i].strip()
                # print(x_pos[i].strip() + " " + y_pos[i].strip())
                context += pos_info + "\n"
            with open(merge_file_path + y_file, 'w') as f:
                f.write(context)


def write_heart_data_to_mysql(file_path):
    files = os.listdir(file_path)
    count = 0
    for heart_file in files:
        heart_file_path = file_path + "/" + heart_file
        start_time = heart_file[0:8].replace('-', ':')
        record_date = "2018-07-14 " + start_time
        record_time = ""
        print(start_time)
        record_heart = record_heart_time(record_date=record_date, start_time=start_time)
        record_heart.save()
        with open(heart_file_path, 'r') as file:
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            for line in data:
                line = line.strip()
                data = line.split(":")
                if len(data) > 1:
                    record_date = "2018-07-14 "
                    record_time = data[0].strip()
                    heart_rate = data[1].strip()
                    record_date += record_time.replace("-", ":")
                    heart_time = record_time[3:].replace("-", ":")
                    average_rate = 0
                    i = 0
                    for rate in heart_rate.split(" "):
                        i += 1
                        average_rate += int(rate)
                    average_rate = int(average_rate / i)
                    # print(record_date)
                    # print(heart_time)
                    # print(heart_rate)
                    # print(average_rate)
                    heart_rate_data = heart_data(record_id=record_heart.id, heart_time=heart_time,
                                                 heart_date=record_date,
                                                 heart_rate=heart_rate, average_rate=average_rate)
                    heart_rate_data.save()
                count += 1
        # print(record_time)
        record_heart.end_time = record_time.replace('-', ':')
        record_heart.save()
    print(count)


def write_beside_data_mysql(file_path):
    files = os.listdir(file_path)
    count = 0
    for heart_file in files:
        heart_file_path = file_path + "/" + heart_file
        start_time = heart_file[0:8].replace("-", ":")
        record_date = "2018-07-14 " + start_time
        print(start_time)
        record_time = ""
        record_shake = record_shake_time(record_date=record_date, start_time=start_time, end_time="")
        record_shake.save()
        with open(heart_file_path, 'r') as file:
            x_data = file.readline()
            while x_data:
                y_data = file.readline()
                x_data = x_data.split(":")
                y_data = y_data.split(":")
                record_time = x_data[0].strip()
                shake_date = "2018-07-14 " + record_time.replace("-", ":")
                shake_time = record_time[3:].replace("-", ":")
                x_data = x_data[2].strip("\n").strip()
                y_data = y_data[2].strip("\n").strip()
                # print(x_data)
                # print(y_data)
                # print(shake_date)
                # print(shake_time)
                shake_record_data = shake_data(record_id=record_shake.id, shake_date=shake_date,
                                               shake_time=shake_time, x_data=x_data, y_data=y_data)
                shake_record_data.save()
                x_data = file.readline()
                count += 1
        record_shake.end_time = record_time.replace("-", ":")
        record_shake.save()
        # print(record_time)
    print(count)


# def write_up_data_to_mysql(file_path):
#     files = os.listdir(file_path)
#     count = 0
#     for heart_file in files:
#         heart_file_path = file_path + "/" + heart_file
#         print(heart_file[0:8])
#         athlete_id = 1
#         game_id = 1
#         with open(heart_file_path, 'r') as file:
#             data = file.readlines()  # 读取全部内容 ，并以列表方式返回
#             for line in data:
#                 record_date = "2018-07-06 " + heart_file[0:3].replace("-", ":")
#                 line = line.strip()
#                 data = line.split(" ")
#                 if len(data) > 1:
#                     up_data = float(data[0])
#                     record_time = data[1]
#                     temp = str(record_time)
#                     record_date += temp[0:5]
#                     print(record_date)
#                     shake_up_data = ShakeUpData(athleteId=athlete_id, gameId=game_id, up_data=up_data,
#                                                 date=record_date, record_time=str(record_time))
#                     shake_up_data.save()
#                 print(line)
#                 count += 1
#     print(count)


def filter_first_data(file_path, save_path):
    files = os.listdir(file_path)
    for heart_file in files:
        heart_file_path = file_path + "/" + heart_file
        print(heart_file[0:8])
        start = int(heart_file[6:8])
        with open(heart_file_path, 'r') as file:
            # context = file.read()
            context = ""
            data = file.readlines()  # 读取全部内容 ，并以列表方式返回
            last = data[-1:][0]
            end = int(last[-6:-4])
            print(last[-6:-4])
            if end - start > 4:
                for line in data:
                    context += line
                with open(save_path + heart_file, 'w') as f:
                    f.write(context)


if __name__ == "__main__":
    # sius时间落后现实时间大约1分27秒
    print("shoot")
    # read_context_from_file('D:\workSpace\PythonWorkspace\shoot\shootweb\data\second\origin\FILE_shoot_2_2018_0714.dat',
    #                        'D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/shoot_2_2018_0714_after_process.dat')
    # write_shoot_grade_to_mysql(
    #     'D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/shoot_2_2018_0714_after_process.dat')

    # read_heart_from_file('D:/workSpace/PythonWorkspace/shoot/shootweb/data/first/origin/heart',
    #                      'D:/workSpace/PythonWorkspace/shoot/shootweb/data/first/second_process/heart/')
    # read_heart_from_file_second('D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/origin/heart',
    #                             'D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/heart/')
    # write_heart_data_to_mysql('D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/heart/')

    # read_camera_from_file('D:/workSpace/PythonWorkspace/shoot/shootweb/data/first/origin/camera/up', 'up',
    #                       'D:/workSpace/PythonWorkspace/shoot/shootweb/data/first/second_process/camera/up/')
    # read_camera_from_file_second('D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/origin/camera/y', 'y',
    #                              'D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/camera/y/')

    read_heart_from_file_third("D:/code/shoot/simulation_data/newdata/Heart")
    read_camera_from_file_third("D:/code/shoot/simulation_data/newdata/Hand")

    # a = "2018-11- 6-10:42:26:231		0.00	1.00";
    # print(find_n_sub_str(a, "-", 2, 0))

    # merge_x_y_to_file('D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/camera/x/',
    #                   'D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/camera/y/',
    #                   'D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/camera/merge/')

    # filter_first_data('D:/workSpace/PythonWorkspace/shoot/shootweb/data/first/second_process/camera/x',
    #                   'D:/workSpace/PythonWorkspace/shoot/shootweb/data/first/third_process/camera/x/')

    # write_beside_data_mysql('D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/camera/merge/')
    # write_up_data_to_mysql('D:/workSpace/PythonWorkspace/shoot/shootweb/data/after_process/camera/up')
    # datatime = "10-21-22"
    # t1 = string_to_time(datatime)
    # print(string_to_time(datatime))
    # print(time_to_string(t1 + datetime.timedelta(minutes=1, seconds=27)))
    # del_file('D:/workSpace/PythonWorkspace/shoot/shootweb/data/second/after_process/camera/y')
    # s = 7.2
    # print(str('%.02f' % s).zfill(5))
    # string = '1,2,3,'
    # a = string.strip(',').split(',')
    # print(a)
    # for s in a:
    #     print(s)
