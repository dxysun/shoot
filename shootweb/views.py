from django.shortcuts import render
from shootweb.models import *
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


def sport_game_analyse(request):
    shoot_reports = shoot_report.objects.all()
    return render(request, 'sport_game_analyse.html', {'shoot_reports': shoot_reports})


def sport_game_analyse_id(request):
    report_id = request.GET['id']
    report = shoot_report.objects.get(id=report_id)
    shake_times = record_shake_time.objects.all()
    record_start = time.strptime(report.shoot_date, "%Y-%m-%d %H:%M:%S")
    report_start_time = time.mktime(record_start)
    end_time = report.shoot_date[:-5] + report.end_time[:5]
    record_end = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    report_end_time = time.mktime(record_end)
    x_data = ""
    y_data = ""
    shoot_info = []
    for shake_time in shake_times:
        record_start = time.strptime(shake_time.record_date, "%Y-%m-%d %H:%M:%S")
        record_start_time = time.mktime(record_start)
        if report_start_time <= record_start_time <= report_end_time:
            shake_datas = shake_data.objects.filter(record_id=shake_time.id)
            for shakeData in shake_datas:
                x_data += shakeData.x_data
                y_data += shakeData.y_data
    shoot_grades = shoot_grade.objects.filter(report_id=report_id)
    grades = ""
    hearts = ""
    r_pos = ""
    p_pos = ""
    for grade in shoot_grades:
        grades += grade.grade + ","
        x = float(grade.x_pos)
        y = float(grade.y_pos)
        r, p = shootlib.cart_to_polar(x, y)
        r = 11 - r
        r_pos += str(r) + ","
        p_pos += str(p) + ","
        heart_times = heart_data.objects.filter(heart_date=grade.grade_date)
        if len(heart_times) == 1:
            heart_time = heart_times[0]
            hearts += str(heart_time.average_rate) + ","
        else:
            hearts += "0,"
        # heart_times = heart_data.objects.get(heart_date=grade.grade_date)
        # if heart_times is not None:
        #     hearts += str(heart_times.average_rate) + ","
        # else:
        #     heart_times += "-1,"
    grades = grades[:-1]
    hearts = hearts[:-1]
    r_pos = r_pos[:-1]
    p_pos = p_pos[:-1]
    return render(request, 'sport_game_analyse_id.html', {
        'shoot_reports': report,
        'grades': grades,
        'hearts': hearts,
        'x_data': x_data[:-1],
        'y_data': y_data[:-1],
        'r_pos': r_pos,
        'p_pos': p_pos
    })


def sport_game_history(request):
    shoot_reports = shoot_report.objects.all()
    # for report in shoot_reports:
    #     shoot_grades = shoot_grade.objects.filter(report_id=report.id)
    #     res = 0
    #     for grade in shoot_grades:
    #         res += int(grade.grade)
    #     report.remark = "5次射击一共" + str(res) + "环"
    #     report.save()
    return render(request, 'sport_game_history.html', {'shoot_reports': shoot_reports})


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
    return render(request, 'index.html')


def coach(request):
    return render(request, 'coach.html')


def vue(request):
    return render(request, 'vue.html', {
        'message1': 'django'
    })
