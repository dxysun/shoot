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
                heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
                if len(heart_times) == 1:
                    heart_time = heart_times[0]
                    heart_temp.append(heart_time.average_rate)
                    heart_total += heart_time.average_rate
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
    # shoot_reports = shoot_report.objects.all()
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
    shake_times = record_shake_time.objects.all()
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
    shoot_info = []
    x_data_five = []
    y_data_five = []
    for shake_time in shake_times:
        record_start = time.strptime(shake_time.record_date + " " + shake_time.record_time, "%Y-%m-%d %H:%M:%S")
        record_start_time = time.mktime(record_start)
        if report_start_time <= record_start_time <= report_end_time:
            shake_datas = shake_data.objects.filter(record_id=shake_time.id)
            x_datas = []
            y_datas = []
            for shakeData in shake_datas:
                x_data += shakeData.x_data
                y_data += shakeData.y_data
                x_datas += shakeData.x_data[:-1].split(",")
                y_datas += shakeData.y_data[:-1].split(",")
            x_data_five, y_data_five = shootlib.get_max_five(x_datas, y_datas)
            x_data_five = list(x_data_five)
    shoot_grades = shoot_grade.objects.filter(report_id=report_id)
    i = 0
    is_have_shake = True
    if len(x_data_five) == 0:
        is_have_shake = False
    for grade in shoot_grades:
        data_info = {}
        data_info['grade_date'] = grade.grade_date
        data_info['grade_time'] = grade.grade_time
        data_info['grade'] = grade.grade
        data_info['rapid_time'] = grade.rapid_time
        data_info['x_pos'] = grade.x_pos
        data_info['y_pos'] = grade.y_pos
        if is_have_shake:
            data_info['x_shake'] = x_data_five[i]
            data_info['y_shake'] = y_data_five[i]
        else:
            data_info['x_shake'] = "0"
            data_info['y_shake'] = "0"
        grades += grade.grade + ","
        x = float(grade.x_pos)
        y = float(grade.y_pos)
        r, p = shootlib.cart_to_polar(x, y)
        r = 11 - r
        r_pos += str(r) + ","
        p_pos += str(p) + ","
        heart_times = heart_data.objects.filter(heart_date=grade.grade_date).filter(heart_time=grade.grade_time)
        if len(heart_times) == 1:
            heart_time = heart_times[0]
            data_info['heart'] = str(heart_time.average_rate)
            hearts += str(heart_time.average_rate) + ","
        else:
            data_info['heart'] = "0"
            hearts += "0,"
        shoot_info.append(data_info)
        i += 1
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
        'p_pos': p_pos,
        'shoot_info': shoot_info
    })


def sport_game_history(request):
    report = shoot_report.objects.last()
    date = report.shoot_date
    shoot_reports = shoot_report.objects.filter(shoot_date=report.shoot_date)
    # for report in shoot_reports:
    #     shoot_grades = shoot_grade.objects.filter(report_id=report.id)
    #     res = 0
    #     for grade in shoot_grades:
    #         res += int(grade.grade)
    #     report.remark = "5次射击一共" + str(res) + "环"
    #     report.save()
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
    return render(request, 'index.html')


def coach(request):
    return render(request, 'coach.html')


def vue(request):
    return render(request, 'vue.html', {
        'message1': 'django'
    })
