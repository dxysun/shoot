from django.shortcuts import render
from shootweb.models import *
from django.http.response import JsonResponse
import time
import math
from . import shootlib


# Create your views here.
def index(request):
    return render(request, 'main.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def main(request):
    return render(request, 'main.html')


def sport_home(request):
    return render(request, 'sport_home.html')


def coach_home(request):
    return render(request, 'coach_home.html')


def coach_sport_info(request):
    return render(request, 'coach_sport_info.html')


def coach_game_info(request):
    return render(request, 'coach_game_info.html')


def coach_sport_info_detail(request):
    return render(request, 'coach_sport_info_detail.html')


def update_data(request):
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
                x_data += shake_time.shake_x_data
                y_data += shake_time.shake_y_data
                x_datas = shake_time.shake_x_data.split(",")
                y_datas = shake_time.shake_y_data.split(",")
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
    dct = {}
    dct['status'] = 'success'
    return JsonResponse(dct)


def sport_game_analyse(request):
    shoot_reports = []
    best_grade = 0
    bad_grade = 100
    total_grade = 0
    num = 0
    average_grade = 0
    quadrant = [0, 0, 0, 0]
    right_up = 0
    left_up = 0
    left_blow = 0
    right_blow = 0
    grades = ""
    r_pos = ""
    p_pos = ""
    hearts = ""
    if request.method == 'POST':
        report_id = request.POST['report_id']
        # print(report_id)
        ids = report_id.split(",")
        for id in ids:
            # print(id)
            num += 1
            report = shoot_report.objects.get(id=id)
            grade = int(report.remark)
            grades += report.remark + ","
            total_grade += grade
            if grade > best_grade:
                best_grade = grade
            if grade < bad_grade:
                bad_grade = grade
            shoot_reports.append(report)
            shoot_grades = shoot_grade.objects.filter(report_id=id)
            heart_temp = []
            heart_total = 0
            for grade in shoot_grades:
                x = float(grade.x_pos)
                y = float(grade.y_pos)
                r, p = shootlib.cart_to_polar(x, y)
                r = 11 - r
                r_pos += str(r) + ","
                p_pos += str(p) + ","
                if x > 0 and y > 0:
                    quadrant[0] += 1
                    right_up += 1
                if x < 0 and y > 0:
                    quadrant[1] += 1
                    left_up += 1
                if x < 0 and y < 0:
                    quadrant[2] += 1
                    left_blow += 1
                if x > 0 and y < 0:
                    quadrant[3] += 1
                    right_blow += 1
                if grade.heart_rate != 0:
                    heart_temp.append(grade.heart_rate)
                    heart_total += grade.heart_rate
            if len(heart_temp) != 0:
                heart = heart_total/len(heart_temp)
            else:
                heart = 0
            hearts += str(heart) + ","
        average_grade = total_grade / num
    grades = grades[:-1]
    r_pos = r_pos[:-1]
    p_pos = p_pos[:-1]
    hearts = hearts[:-1]
    return render(request, 'sport_game_analyse.html', {
        'shoot_reports': shoot_reports,
        'best_grade': best_grade,
        'bad_grade': bad_grade,
        'average_grade': average_grade,
        'quadrant': quadrant,
        'right_up': right_up,
        'left_up': left_up,
        'left_blow': left_blow,
        'right_blow': right_blow,
        'grades': grades,
        'r_pos': r_pos,
        'p_pos': p_pos,
        'hearts': hearts
    })


def sport_game_analyse_id(request):
    report_id = request.GET['id']
    report = shoot_report.objects.get(id=report_id)
    grades = ""
    hearts = ""
    r_pos = ""
    p_pos = ""
    shoot_grades = shoot_grade.objects.filter(report_id=report_id)
    is_have_shake = True
    for grade in shoot_grades:
        grades += grade.grade + ","
        x = float(grade.x_pos)
        y = float(grade.y_pos)
        r, p = shootlib.cart_to_polar(x, y)
        r = 11 - r
        r_pos += str(r) + ","
        p_pos += str(p) + ","
        hearts += str(grade.heart_rate) + ","
    grades = grades[:-1]
    hearts = hearts[:-1]
    r_pos = r_pos[:-1]
    p_pos = p_pos[:-1]
    return render(request, 'sport_game_analyse_id.html', {
        'shoot_reports': report,
        'grades': grades,
        'hearts': hearts,
        'x_data': report.x_shake_data,
        'y_data': report.y_shake_data,
        'r_pos': r_pos,
        'p_pos': p_pos,
        'shoot_info': shoot_grades
    })


def sport_game_history(request):
    report = shoot_report.objects.last()
    date = report.shoot_date
    shoot_reports = shoot_report.objects.filter(shoot_date=report.shoot_date)
    return render(request, 'sport_game_history.html', {
        'shoot_reports': shoot_reports,
        'date': date
    })


def admin_home(request):
    return render(request, 'admin_home.html')


def admin_coach(request):
    return render(request, 'admin_coach.html')


def admin_sport(request):
    return render(request, 'admin_sport.html')


def admin_add_item(request):
    return render(request, 'admin_add_item.html')


def admin_add_coach(request):
    return render(request, 'admin_add_coach.html')


def admin_add_sport(request):
    return render(request, 'admin_add_sport.html')


def test(request):
    return render(request, 'convert.html')


def coach(request):
    return render(request, 'coach.html')


def vue(request):
    return render(request, 'vue.html', {
        'message1': 'django'
    })
