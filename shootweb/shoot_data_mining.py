# -*- coding:utf-8 -*- 
__author__ = 'dxy'
import sys
import os
import django
import time
import datetime
import math
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd

dirname, filename = os.path.split(os.path.abspath(__file__))
pre_path = os.path.abspath(os.path.dirname(dirname))
sys.path.append(pre_path + '/shoot')
os.chdir(pre_path + '/shoot')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot.settings")
django.setup()
from shootweb.models import *


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
        report_df.loc[r_i] = [report.id, report.shoot_date, report.shoot_time, report.start_time, report.end_time,
                              float(report.total_grade), int(report.remark), report.x_shake_data, report.y_shake_data,
                              report.x_shake_pos, report.y_shake_pos, report.x_up_shake_data, report.y_up_shake_data,
                              report.x_up_shake_pos, report.y_up_shake_pos]
        r_i += 1
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
        for grade in shoot_grades:
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
        print()
    report_df.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/report_info.xlsx")
    grade_df.to_excel("D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_info.xlsx")


def save_grade_info():
    shoot_grades = shoot_grade.objects.all()
    print(len(shoot_grades))
    for grade in shoot_grades:
        if 's' in grade.rapid_time:
            print(grade.grade_detail_time)
            print(grade.rapid_time)
            print()


if __name__ == "__main__":
    print()
    # save_report_info()
    # save_grade_info()
