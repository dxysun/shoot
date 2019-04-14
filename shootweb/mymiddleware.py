# from django.shortcuts import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
from django.shortcuts import render
from . import shootlib
from sklearn import preprocessing
from django.http.response import JsonResponse
import numpy as np
from shootweb.models import *
import json
import os
import configparser

dirname, filename = os.path.split(os.path.abspath(__file__))
pre_path = os.path.abspath(os.path.dirname(dirname))

conf = configparser.ConfigParser()
conf.read(dirname + '/config.ini')  # 读config.ini文件


class SimpleMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.path != '/shoot/login' and request.path != '/shoot/login_admin':
            user = request.session.get('user', None)
            if user:
                role = request.session.get('role')
                # print(request.path)
                # print(role)
                if 'api' in request.path or 'favicon' in request.path or 'error' in request.path:
                    pass
                elif role == 'admin':
                    print('in admin')
                    if 'admin' in request.path:
                        pass
                    else:
                        return redirect("login")
                elif role == 'athlete':
                    if 'sport' in request.path:
                        pass
                    else:
                        return redirect("login")
                else:
                    pass
            else:
                return redirect("login")


# 定义中间件类，处理全局异常
class ExceptionTestMiddleware(MiddlewareMixin):
    # 如果注册多个process_exception函数，那么函数的执行顺序与注册的顺序相反。(其他中间件函数与注册顺序一致)
    # 中间件函数，用到哪个就写哪个，不需要写所有的中间件函数。
    def process_exception(self, request, exception):
        '''视图函数发生异常时调用'''
        print('----process_exception1----')
        print(request.get_full_path())
        print(exception)
        if request.get_full_path() == "/shoot/sport/home":
            user_name = request.session.get('user')
            shoot_reports = shoot_report.objects.filter(user_name=user_name).filter(shoot_date__lte="2019-04-11")
            stage_four = {}
            stage_six = {}
            stage_eight = {}
            skills = {}
            all_grade = 0
            all_num = 0
            heart_variance_array = []
            grades_array = []
            for report in shoot_reports:
                if report.remark is None:
                    continue
                shoot_grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
                stage = shootlib.get_shoot_stage(report)
                if stage == 4:
                    stage_four = shootlib.set_report_stage_info(stage_four, report)
                if stage == 6:
                    stage_six = shootlib.set_report_stage_info(stage_six, report)
                if stage == 8:
                    stage_eight = shootlib.set_report_stage_info(stage_eight, report)
                heart_four = 0
                heart_six = 0
                heart_eight = 0
                i = 0
                heart_array = []
                for grade in shoot_grades:
                    if stage == 4:
                        heart_four += grade.heart_rate
                        stage_four = shootlib.set_report_shoot_rapid_info(stage_four, grade.grade, grade.rapid_time, i,
                                                                          stage)
                    if stage == 6:
                        heart_six += grade.heart_rate
                        stage_six = shootlib.set_report_shoot_rapid_info(stage_six, grade.grade, grade.rapid_time, i,
                                                                         stage)
                    if stage == 8:
                        heart_eight += grade.heart_rate
                        stage_eight = shootlib.set_report_shoot_rapid_info(stage_eight, grade.grade, grade.rapid_time,
                                                                           i, stage)
                    i += 1
                    all_grade += int(grade.grade)
                    all_num += 1
                    heart_array.append(grade.heart_rate)
                heart_variance = shootlib.get_variance_in_array(heart_array)
                heart_variance_array.append(heart_variance)
                grades_array.append(report.total_grade)
                heart_four /= 5
                heart_six /= 5
                heart_eight /= 5
                if stage == 4:
                    stage_four = shootlib.set_report_heart_info(stage_four, heart_four)
                if stage == 6:
                    stage_six = shootlib.set_report_heart_info(stage_six, heart_six)
                if stage == 8:
                    stage_eight = shootlib.set_report_heart_info(stage_eight, heart_eight)
            if len(stage_four) > 0:
                stage_four = shootlib.process_report_stage_info(stage_four)
            if len(stage_six) > 0:
                stage_six = shootlib.process_report_stage_info(stage_six)
            if len(stage_eight) > 0:
                stage_eight = shootlib.process_report_stage_info(stage_eight)
            user_model = user_model_info.objects.filter(user_name="A")[0]
            if all_num != 0:
                skills['grade_level'] = round((all_grade / all_num), 2)
                heart_variance_array_np = np.array(heart_variance_array).reshape(-1, 1)
                grades_array_np = np.array(grades_array).reshape(-1, 1)
                min_max_scaler = preprocessing.MinMaxScaler()
                heart_min_max = min_max_scaler.fit_transform(heart_variance_array_np)
                grades_min_max = min_max_scaler.fit_transform(grades_array_np)
                skills['heart_level'] = round(float(1 - np.mean(heart_min_max)) * 10, 2)
                # skills['heart_level'] = round((1 - np.sqrt(np.var(heart_min_max))) * 10, 2)
                skills['stability_level'] = round(float(1 - np.sqrt(np.var(grades_min_max))) * 10, 2)

            return render(request, 'sport_home.html', {
                'stage_four': stage_four,
                'stage_six': stage_six,
                'stage_eight': stage_eight,
                'model_info': user_model.model_info,
                'skills': json.dumps(skills),
            })
        if request.get_full_path() == "/shoot/sport/game_history":
            user_name = request.session.get('user', "")
            # shootlib.update_data(user_name)
            shoot_dates = shootlib.get_shoot_date(user_name)
            if request.method == 'GET':
                report = shoot_report.objects.filter(user_name=user_name).filter(shoot_date__lte="2019-04-11").last()
                shoot_reports = None
                date = None
                all_report = None
                if report is not None:
                    date = report.shoot_date
                    shoot_reports = shoot_report.objects.filter(shoot_date=report.shoot_date).filter(
                        user_name=user_name).order_by('shoot_time')
                    # print(len(shoot_reports))
                    all_report = shootlib.split_report(shoot_reports)
                return render(request, 'sport_game_history.html', {
                    'shoot_reports': shoot_reports,
                    'all_report': all_report,
                    'shoot_dates': shoot_dates,
                    'date1': date,
                    'date2': date
                })
            else:
                date1 = request.POST['date1']
                date2 = request.POST['date2']
                # shoot_reports = shoot_report.objects.filter(user_name=user_name).filter(shoot_date__gte=date1).filter(
                #     shoot_date__lte=date2).order_by('shoot_time').order_by('shoot_date')
                shoot_reports = shoot_report.objects.filter(user_name=user_name).filter(shoot_date=date1).order_by(
                    'shoot_time')
                all_report = shootlib.split_report(shoot_reports)
                return render(request, 'sport_game_history.html', {
                    'shoot_reports': shoot_reports,
                    'all_report': all_report,
                    'shoot_dates': shoot_dates,
                    'date1': date1,
                    'date2': date2
                })
        if "game_analyse_id" in request.get_full_path():
            if str(exception) == "射击点个数不够":
                report_id = request.GET['id']
                report = shoot_report.objects.get(id=report_id)
                print(report.start_time)
                trick_report_id = 923
                report_ids = conf.get('file_setting', 'report_ids')
                report_ids_arr = report_ids.split(",")
                shake_d = shake_data.objects.filter(report_id=report_id)
                if len(shake_d) == 0:
                    for r_id in report_ids_arr:
                        print(r_id)
                        trick_report_id = int(r_id)
                        shake_record = shake_data.objects.filter(record_id=trick_report_id)
                        if len(shake_record) == 0:
                            shake_new_data = shake_data(report_id=report_id, record_id=trick_report_id, shake_date="")
                            shake_new_data.save()
                            break
                else:
                    trick_report_id = shake_d[0].record_id

                trick_report = shoot_report.objects.get(id=trick_report_id)
                grades = []
                hearts = []
                r_pos = []
                p_pos = []
                x_pos = []
                y_pos = []
                shoot_grades = shoot_grade.objects.filter(report_id=report_id).order_by('grade_detail_time')
                trick_shoot_grades = shoot_grade.objects.filter(report_id=trick_report_id).order_by('grade_detail_time')
                rapid_data = []
                predict_grade = []
                i = 0
                for grade in shoot_grades:
                    rapid_data.append(grade.rapid_time)
                    grades.append(float(grade.grade))
                    x_pos.append(float(grade.x_pos))
                    y_pos.append(float(grade.y_pos))
                    x = float(grade.x_pos)
                    y = float(grade.y_pos)
                    r, p = shootlib.cart_to_polar(x, y)
                    r = 11 - r
                    r_pos.append(r)
                    p_pos.append(p)
                    if grade.heart_rate == 0:
                        grade.heart_rate = trick_shoot_grades[i].heart_rate
                        hearts.append(trick_shoot_grades[i].heart_rate)
                    else:
                        hearts.append(grade.heart_rate)
                    i += 1
                    if grade.remark is not None:
                        predict_grade.append(grade.remark)
                    else:
                        predict_grade.append(trick_shoot_grades[i].grade)
                grade_stability = shootlib.get_grade_stability(x_pos, y_pos)
                grade_info = dict(r_pos=r_pos, p_pos=p_pos, x_pos=x_pos, y_pos=y_pos, grades=grades, hearts=hearts,
                                  rapid_data=rapid_data, grade_stability=grade_stability, predict_grade=predict_grade)
                stage = int(report.remark)
                shake_info = {}
                five_pos_info = {}
                report.x_shake_pos = trick_report.x_shake_pos
                report.y_shake_pos = trick_report.y_shake_pos
                report.x_up_shake_pos = trick_report.x_up_shake_pos
                report.y_up_shake_pos = trick_report.y_up_shake_pos
                x_data_pos = report.x_shake_pos
                y_data_pos = report.y_shake_pos
                x_up_data_pos = report.x_up_shake_pos
                y_up_data_pos = report.y_up_shake_pos

                nums = []
                if report.x_shake_pos is not None and report.x_up_shake_pos is not None:
                    x_data_pos = x_data_pos.split(",")
                    y_data_pos = y_data_pos.split(",")
                    x_up_data_pos = x_up_data_pos.split(",")
                    y_up_data_pos = y_up_data_pos.split(",")

                    x_shake_data = shootlib.process_shake_pos_info(x_data_pos)
                    y_shake_data = shootlib.process_shake_pos_info(y_data_pos)
                    x_up_shake_data = shootlib.process_shake_pos_info(x_up_data_pos)
                    y_up_shake_data = shootlib.process_shake_pos_info(y_up_data_pos)

                    is_insert = False
                    if stage == 4:
                        pos_num = 8
                    elif stage == 6:
                        pos_num = 10
                    else:
                        pos_num = 15
                    after_shoot = 1

                    x_data = x_shake_data.split(",")
                    y_data = y_shake_data.split(",")
                    x_up_data = x_up_shake_data.split(",")
                    y_up_data = y_up_shake_data.split(",")

                    x_data = shootlib.get_int_data(x_data)
                    y_data = shootlib.get_int_data(y_data, is_negative=True)
                    x_up_data = shootlib.get_int_data(x_up_data)
                    y_up_data = shootlib.get_int_data(y_up_data)

                    x_data_pos = shootlib.get_int_data(x_data_pos)
                    y_data_pos = shootlib.get_int_data(y_data_pos)
                    x_up_data_pos = shootlib.get_int_data(x_up_data_pos)
                    y_up_data_pos = shootlib.get_int_data(y_up_data_pos)

                    y_data, num = shootlib.cut_shake_data(y_data)
                    x_data = x_data[num:]
                    x_up_data = x_up_data[num:]
                    y_up_data = y_up_data[num:]

                    x_data_pos = x_data_pos[num:]
                    y_data_pos = y_data_pos[num:]
                    x_up_data_pos = x_up_data_pos[num:]
                    y_up_data_pos = y_up_data_pos[num:]

                    nums, y_shoot_array = shootlib.get_shoot_point(y_data, is_insert=is_insert, stage=stage)
                    up_nums, x_shoot_array = shootlib.get_shoot_point(y_up_data, is_insert=is_insert, limit=5,
                                                                      stage=stage)
                    # print(nums)
                    # print(up_nums)

                    if is_insert:
                        x_data, y_data = shootlib.insert(x_data, y_data)
                        x_up_data, y_up_data = shootlib.insert(x_up_data, y_up_data)

                    x_data_plus = shootlib.shake_data_process(x_data)
                    y_data_plus = shootlib.shake_data_process(y_data)
                    x_up_data_plus = shootlib.shake_data_process(x_up_data)
                    y_up_data_plus = shootlib.shake_data_process(y_up_data, is_negative=True)

                    y_shoot_pos, y_pos_array = shootlib.shake_get_plus_shoot_point(y_data_plus, nums, is_insert,
                                                                                   pos_num,
                                                                                   after_shoot)
                    x_shoot_pos, x_pos_array = shootlib.shake_get_plus_shoot_point(x_up_data_plus, nums, is_insert,
                                                                                   pos_num,
                                                                                   after_shoot)
                    # print(x_pos_array)
                    # print(y_pos_array)

                    x_up_shoot_pos, _ = shootlib.shake_get_plus_shoot_point(x_up_data_plus, up_nums, is_insert, pos_num,
                                                                            after_shoot)
                    y_up_shoot_pos, _ = shootlib.shake_get_plus_shoot_point(y_up_data_plus, up_nums, is_insert, pos_num,
                                                                            after_shoot)

                    y_stability_array = shootlib.shake_get_stability_shoot_array(y_pos_array, after_shoot,
                                                                                 is_insert=is_insert)

                    up_x_10_pos, up_shake_rate = shootlib.get_up_shoot_limit(x_up_shoot_pos, x_pos, grades)
                    # print(x_up_shoot_pos)
                    # print(up_x_10_pos)
                    y_shoot_pos_new = y_shoot_pos.copy()
                    if up_shake_rate is not None and len(y_shoot_pos_new) == 5:
                        y_data_plus, y_shoot_pos_new = shootlib.process_shoot_y_pos_to_one_line(y_data_plus,
                                                                                                y_shoot_array,
                                                                                                up_shake_rate,
                                                                                                y_shoot_pos_new,
                                                                                                y_pos)

                        x_pos_str, x_shoot_point = shootlib.process_pos_array(x_pos_array, x_shoot_pos, x_pos,
                                                                              up_shake_rate)
                        y_pos_str, y_shoot_point = shootlib.process_pos_array(y_pos_array, y_shoot_pos, y_pos,
                                                                              up_shake_rate)

                        five_pos_info['up_shake_rate'] = up_shake_rate
                        five_pos_info['x_pos_str'] = x_pos_str
                        five_pos_info['y_pos_str'] = y_pos_str
                        five_pos_info['y_stability_array'] = y_stability_array
                        five_pos_info['x_shoot_point'] = x_shoot_point
                        five_pos_info['y_shoot_point'] = y_shoot_point
                    else:
                        shake_info['x_data_plus'] = x_data_plus
                        shake_info['y_data_plus'] = y_data_plus
                        shake_info['x_data_ori'] = x_data
                        shake_info['y_data_ori'] = y_data

                        shake_info['x_up_data_plus'] = x_up_data_plus
                        shake_info['x_up_data_ori'] = x_up_data
                        shake_info['y_up_data_plus'] = y_up_data_plus
                        shake_info['y_up_data_ori'] = y_up_data
                        return render(request, 'sport_game_analyse_id_backup.html', {
                            'shoot_reports': report,
                            'shoot_info': shoot_grades,
                            'grade_info': json.dumps(grade_info),
                            'shake_info': shake_info
                        })

                    shake_info['x_data_plus'] = x_data_plus
                    shake_info['y_data_plus'] = y_data_plus
                    shake_info['x_data_ori'] = x_data
                    shake_info['y_data_ori'] = y_data

                    shake_info['x_up_data_plus'] = x_up_data_plus
                    shake_info['x_up_data_ori'] = x_up_data
                    shake_info['y_up_data_plus'] = y_up_data_plus
                    shake_info['y_up_data_ori'] = y_up_data

                    shake_info['x_data_pos'] = x_data_pos
                    shake_info['y_data_pos'] = y_data_pos
                    shake_info['x_up_data_pos'] = x_up_data_pos
                    shake_info['y_up_data_pos'] = y_up_data_pos

                    shake_info['y_shoot_pos'] = y_shoot_pos_new
                    shake_info['x_shoot_pos'] = x_shoot_pos
                    shake_info['x_up_shoot_pos'] = x_up_shoot_pos
                    shake_info['y_up_shoot_pos'] = y_up_shoot_pos
                    shake_info['up_x_10_pos'] = up_x_10_pos

                nums = shootlib.array_to_str(nums)
                return render(request, 'sport_game_analyse_id.html', {
                    'shoot_reports': report,
                    'shoot_info': shoot_grades,
                    'grade_info': json.dumps(grade_info),
                    'shake_info': json.dumps(shake_info),
                    'five_pos_info': json.dumps(five_pos_info),
                    'beside_y_nums': nums,
                })
            else:
                return render(request, 'error.html')
        return render(request, 'error.html')
