from watchdog.observers import Observer
from watchdog.events import *
import time
import sys
import os
import datetime
import django
import threading
import configparser
import inspect
import ctypes

dirname, filename = os.path.split(os.path.abspath(__file__))
pre_path = os.path.abspath(os.path.dirname(dirname))

sys.path.append(pre_path + '/shoot')
os.chdir(pre_path + '/shoot')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot.settings")
django.setup()
from shootweb.models import *

conf = configparser.ConfigParser()
conf.read(dirname + '/config.ini')  # 读config.ini文件


def follow(the_file):
    the_file.seek(0, 2)
    while True:
        line = the_file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def time_to_string_mill(dt):
    return dt.strftime("%H:%M:%S.%f")


def string_to_time_mill(string):
    return datetime.datetime.strptime(string, "%H:%M:%S.%f")


class GradeEventHandler(FileSystemEventHandler):
    def __init__(self, username):
        FileSystemEventHandler.__init__(self)
        self.grade_file = None
        self.num = 0
        self.report_data = None
        self.shoot_data = None
        self.start_time = ''
        self.end_time = ''
        self.username = username
        self.total_grade = 0

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))

    def set_username(self, username):
        self.username = username

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))
            if self.grade_file is None:
                self.grade_file = open(event.src_path, "r", encoding='ISO-8859-15')
            else:
                while True:
                    line = self.grade_file.readline()
                    if not line:
                        break
                    if line.find("Shot Report") != -1:
                        line = "Shot Report"
                    elif 'Miss' in line:
                        continue
                    elif line.find("P") != -1:
                        i = line.find("P")
                        if line[i - 2] == "0":
                            line = line[i - 3:].strip()
                        else:
                            line = line[i - 2:].strip()
                    else:
                        line = line.strip()
                    print(line)
                    d = datetime.datetime.now().strftime("%Y-%m-%d")
                    if line == "Shot Report":
                        print(self.username)
                        self.report_data = shoot_report(shoot_date=d, start_time=self.start_time,
                                                        end_time=self.end_time, user_name=self.username)
                        self.report_data.save()
                        self.num = 0
                        self.total_grade = 0
                    else:
                        if self.report_data is not None and self.num < 10:
                            self.num += 1
                            if 'P' in line:
                                i = line.find('P')
                                grade = line[:i - 1]
                                line = line[i + 1:]
                                lines = line.split()
                                # print(str(lines))
                                shoot_time = lines[0]
                                if self.num == 1:
                                    self.end_time = shoot_time
                                if self.num == 9:
                                    self.start_time = shoot_time
                                x_pos = lines[1][:-1]
                                y_pos = lines[2]
                                t = datetime.datetime.now().strftime("%H:")
                                t += shoot_time[0:5]
                                self.total_grade += int(grade)
                                self.shoot_data = shoot_grade(report_id=self.report_data.id, grade_date=d,
                                                              grade_time=t, grade_detail_time=shoot_time,
                                                              grade=grade, rapid_time="", x_pos=x_pos, y_pos=y_pos,
                                                              user_name=self.username)
                                self.shoot_data.save()
                            else:
                                if self.shoot_data is not None:
                                    rapid_time = line[1:-1]
                                    self.shoot_data.rapid_time = rapid_time
                                    self.shoot_data.save()
                                    self.shoot_data = None
                            if self.num >= 10:
                                if self.num == 10:
                                    self.report_data.start_time = self.start_time
                                    self.report_data.end_time = self.end_time
                                    self.report_data.remark = str(self.total_grade)
                                    t = datetime.datetime.now().strftime("%H:")
                                    t += self.start_time[0:5]
                                    self.report_data.shoot_time = t
                                    self.end_time = ""
                                    self.start_time = ""
                                    self.report_data.save()
                                    self.report_data = None
                                self.num += 1


class GradeEventOldTimerHandler(FileSystemEventHandler):
    def __init__(self, username):
        FileSystemEventHandler.__init__(self)
        self.grade_file = None
        self.num = 0
        self.report_data = None
        self.shoot_data = None
        self.start_time = ''
        self.end_time = ''
        self.rapid_time = ''
        self.username = username
        self.total_grade = 0
        file_path = conf.get('file_setting', 'grade_file')
        line_num = conf.get('file_setting', 'line_num')
        if os.path.exists(file_path):
            print("file exist")
            self.grade_file = open(file_path, "r", encoding='ISO-8859-15')
            self.thread = threading.Thread(target=self.listen, args=(file_path, int(line_num)))
            self.thread.start()
        else:
            print("file not exist")
            self.thread = None

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))
            if self.thread is not None:
                stop_thread(self.thread)
                self.grade_file.close()
                self.thread = None
            self.grade_file = open(event.src_path, "r", encoding='ISO-8859-15')
            self.thread = threading.Thread(target=self.listen, args=(event.src_path,))
            self.thread.start()

    def set_username(self, username):
        self.username = username

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))

    def listen(self, path, line_num=-1):
        print("line_num:" + str(line_num))
        if (self.grade_file is not None) and (line_num != -1):
            for i in range(0, line_num):
                self.grade_file.readline()
        if self.grade_file is None:
            print("self.grade_file none")
        conf.set('file_setting', 'grade_file', path)
        if line_num == -1:
            line_num = line_num + 1
        num = line_num
        while True:
            if self.grade_file is None:
                self.grade_file = open(path, "r", encoding='ISO-8859-15')
            else:
                line = self.grade_file.readline()
                conf.set('file_setting', 'line_num', str(num))
                conf.write(open(dirname + '/config.ini', "w"))
                if not line:
                    time.sleep(4)
                    continue
                num += 1
                d = datetime.datetime.now().strftime("%Y-%m-%d")
                if line.find("Shot Report") != -1:
                    line = "Shot Report"
                elif 'Miss' in line:
                    continue
                elif line.find("P") != -1:
                    i = line.find("P")
                    if line[i - 2] == "0":
                        line = line[i - 3:].strip()
                    else:
                        line = line[i - 2:].strip()
                else:
                    line = line.strip()
                print(line)
                d = datetime.datetime.now().strftime("%Y-%m-%d")
                if line == "Shot Report":
                    print(self.username)
                    self.report_data = shoot_report(shoot_date=d, start_time=self.start_time,
                                                    end_time=self.end_time, user_name=self.username)
                    self.report_data.save()
                    self.num = 0
                    self.total_grade = 0
                else:
                    if self.report_data is not None and self.num < 10:
                        self.num += 1
                        if 'P' in line:
                            i = line.find('P')
                            grade = line[:i - 1]
                            line = line[i + 1:]
                            lines = line.split()
                            # print(str(lines))
                            shoot_time = lines[0]
                            if self.num == 1:
                                self.end_time = shoot_time
                            if self.num == 9:
                                self.start_time = shoot_time
                            x_pos = lines[1][:-1]
                            y_pos = lines[2]
                            t = datetime.datetime.now().strftime("%H:")
                            t += shoot_time[0:5]
                            self.total_grade += int(grade)
                            self.shoot_data = shoot_grade(report_id=self.report_data.id, grade_date=d,
                                                          grade_time=t, grade_detail_time=shoot_time,
                                                          grade=grade, rapid_time="", x_pos=x_pos, y_pos=y_pos,
                                                          user_name=self.username)
                            self.shoot_data.save()
                        else:
                            if self.shoot_data is not None:
                                rapid_time = line[1:-1]
                                self.rapid_time = rapid_time[:-1]
                                self.shoot_data.rapid_time = self.rapid_time
                                self.shoot_data.save()
                                self.shoot_data = None
                        if self.num >= 10:
                            if self.num == 10:
                                self.report_data.remark = str(self.total_grade)
                                t = datetime.datetime.now().strftime("%H:")
                                self.start_time = t + self.start_time
                                self.end_time = t + self.end_time
                                self.report_data.shoot_time = self.start_time
                                report_time = time_to_string_mill(
                                    string_to_time_mill(self.start_time) - datetime.timedelta(
                                        seconds=float(self.rapid_time)))
                                self.report_data.start_time = report_time[:-4]
                                self.report_data.end_time = self.end_time
                                self.report_data.save()
                                self.end_time = ""
                                self.rapid_time = ""
                                self.start_time = ""
                                self.report_data = None
                            self.num += 1


class GradeEventTimerHandler(FileSystemEventHandler):
    def __init__(self, username):
        FileSystemEventHandler.__init__(self)
        self.grade_file = None
        self.num = 0
        self.report_data = None
        self.shoot_data = None
        self.start_time = ''
        self.end_time = ''
        self.rapid_time = ''
        self.username = username
        self.is_report = False
        self.total_grade = 0
        file_path = conf.get('file_setting', 'grade_file')
        line_num = conf.get('file_setting', 'line_num')
        if os.path.exists(file_path):
            print("file exist")
            self.grade_file = open(file_path, "r", encoding='ISO-8859-15')
            self.thread = threading.Thread(target=self.listen, args=(file_path, int(line_num)))
            self.thread.start()
        else:
            print("file not exist")
            self.thread = None

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))
            if self.thread is not None:
                stop_thread(self.thread)
                self.grade_file.close()
                self.thread = None
            self.grade_file = open(event.src_path, "r", encoding='ISO-8859-15')
            self.thread = threading.Thread(target=self.listen, args=(event.src_path,))
            self.thread.start()

    def set_username(self, username):
        self.username = username

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))

    def listen(self, path, line_num=-1):
        print("line_num:" + str(line_num))
        if (self.grade_file is not None) and (line_num != -1):
            for i in range(0, line_num):
                self.grade_file.readline()
        if self.grade_file is None:
            print("self.grade_file none")
        conf.set('file_setting', 'grade_file', path)
        if line_num == -1:
            line_num = line_num + 1
        l_num = line_num
        while True:
            if self.grade_file is None:
                self.grade_file = open(path, "r", encoding='ISO-8859-15')
            else:
                line = self.grade_file.readline()
                conf.set('file_setting', 'line_num', str(l_num))
                conf.write(open(dirname + '/config.ini', "w"))
                if not line:
                    time.sleep(4)
                    continue
                l_num += 1
                line = line.strip()
                print(line)
                d = datetime.datetime.now().strftime("%Y-%m-%d")
                if self.is_report:
                    if self.report_data is not None and self.num < 10:
                        self.num += 1
                        if 'Miss' in line:
                            self.num += 1
                            continue
                        if '/' in line:
                            data = line.split("/")
                            # print(data)
                            y_pos = data[1].strip()
                            data = data[0].split()
                            x_pos = data[-1]
                            shoot_time = data[-2]
                            grade = None
                            if data[-3].isdigit():
                                grade = data[-3]
                            else:
                                if data[-3] == "P":
                                    grade = data[-4]
                                elif "*P" in data[-3]:
                                    grade = data[-3][:-2]
                                elif "*" in data[-3]:
                                    grade = data[-3][:-1]
                            t1 = datetime.datetime.now().strftime("%H:")
                            t = t1 + shoot_time[0:5]
                            if self.num == 1:
                                self.end_time = shoot_time
                            if self.num == 9:
                                self.start_time = shoot_time
                            self.total_grade += float(grade)
                            self.shoot_data = shoot_grade(report_id=self.report_data.id, grade_date=d,
                                                          grade_time=t, grade_detail_time=t1 + shoot_time,
                                                          grade=grade, rapid_time="", x_pos=x_pos, y_pos=y_pos,
                                                          user_name=self.username)
                            print("save shoot_data")
                            self.shoot_data.save()
                        else:
                            if self.shoot_data is not None:
                                rapid_time = line[1:-1]
                                s = rapid_time.find("s")
                                self.rapid_time = rapid_time[:s]
                                self.shoot_data.rapid_time = self.rapid_time
                                self.shoot_data.save()
                                self.shoot_data = None
                    if self.num >= 10:
                        if self.num == 10:
                            self.report_data.total_grade = self.total_grade
                            t = datetime.datetime.now().strftime("%H:")
                            # print("start_time:" + str(self.start_time))
                            self.start_time = t + self.start_time
                            self.end_time = t + self.end_time
                            self.report_data.shoot_time = self.start_time
                            print(self.start_time)
                            report_time = time_to_string_mill(
                                string_to_time_mill(self.start_time) - datetime.timedelta(
                                    seconds=float(self.rapid_time)))
                            self.report_data.start_time = report_time[:-4]
                            self.report_data.end_time = self.end_time
                            print("save report_data")
                            self.report_data.save()
                            self.is_report = False
                            self.end_time = ""
                            self.rapid_time = ""
                            self.start_time = ""
                            self.report_data = None
                        self.num += 1
                else:
                    if line.find("Shot Report") != -1:
                        self.is_report = True
                        print(self.username)
                        self.report_data = shoot_report(shoot_date=d, start_time=self.start_time,
                                                        end_time=self.end_time, user_name=self.username)
                        self.report_data.save()
                        print("save first report_data")
                        self.num = 0
                        self.total_grade = 0


def start_watch(username):
    observer1 = Observer()
    event_handler = GradeEventTimerHandler(username)
    observer1.schedule(event_handler, "D:/grade", True)
    # observer1.schedule(event_handler, "D:\code\shoot\simulation_data\grade", True)
    observer1.start()
    return observer1


if __name__ == "__main__":
    print()
    # observer = start_watch("A")
    # time.sleep(30)
    # print("set username B")
    # observer.username = "B"
    # print(observer.username)
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()
    # print(conf.get('file_setting', 'grade_file'))
    # conf.set('file_setting', 'grade_file', 'filekkkkkk')
    # conf.write(open(cur_path + '/config.ini', "w"))
    # print(conf.get('file_setting', 'grade_file'))
