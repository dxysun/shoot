from django.shortcuts import render
from shootweb.models import *
from django.http.response import JsonResponse
import time
import math
from . import shootlib
from django.shortcuts import redirect


# Create your views here.
def index(request):
    return render(request, 'main.html')


def login_admin(request):
    if request.method == 'GET':
        return render(request, 'login_admin.html')
    result = {}
    if request.method == "POST":  # 请求方法为POST时，进行处理
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = user_info.objects.filter(user_name=username)
        if len(user) == 0:
            result["status"] = "failed"
        elif user[0].password == password:
            request.session["username"] = username
            request.session["user_id"] = user[0].id
            request.session["user"] = "admin"
            request.session["role"] = "admin"
            result["status"] = "success"
        else:
            result["status"] = "failed"
        return JsonResponse(result)


def get_user_info(request):
    if request.method == 'POST':
        users = user_info.objects.filter(role="athlete")
        result={}
        result['data'] = []
        for user  in users:
            u = {}
            u['id'] = user.id
            u['user_name'] = user.user_name
            result['data'].append(u)
        if len(users) > 0:
            result["status"] = "success"
        else:
            result["status"] = "failed"
        return JsonResponse(result)


def login(request):
    if request.method == 'GET':
        users = user_info.objects.filter(role="athlete")
        return render(request, 'login.html', {
            "users": users
        })
    if request.method == 'POST':
        user_id = request.POST['user_id']
        user = user_info.objects.get(id=int(user_id))
        print(user_id)
        request.session['user'] = user.user_name
        request.session['user_id'] = user.id
        request.session['role'] = user.role
        return redirect("sport_home")


def logout(request):
    del request.session["user"]
    del request.session["role"]
    del request.session["user_id"]
    return redirect("login")


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
    user_name = request.session.get('user',"")
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
                shake_time.user_name = user_name
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
            grade.user_name = user_name
            grade.save()
            i += 1
        report.is_process = 1
        report.user_name = user_name
        report.save()
    dct = {}
    dct['status'] = 'success'
    return JsonResponse(dct)


def sport_game_analyse(request):
    user_name = request.session.get('user', "")
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
                heart = heart_total / len(heart_temp)
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
    user_name = request.session.get('user',"")
    report = shoot_report.objects.last()
    date = report.shoot_date
    shoot_reports = shoot_report.objects.filter(shoot_date=report.shoot_date).filter(user_name=user_name)
    return render(request, 'sport_game_history.html', {
        'shoot_reports': shoot_reports,
        'date': date
    })


def admin_home(request):
    if request.method == 'POST':
        item_name = request.POST['item_name']
        item_intro = request.POST['item_intro']
        item_rule = request.POST['item_rule']
        print(item_name)
        shoot_item = shoot_items(item_name=item_name, item_info=item_intro, item_rule=item_rule)
        shoot_item.save()
    items = shoot_items.objects.all()
    all_item = []
    for item in items:
        info = {}
        info["id"] = item.id
        info["item_name"] = item.item_name
        coachs = user_info.objects.filter(item_id=item.id).filter(role="coach")
        athletes = user_info.objects.filter(item_id=item.id).filter(role="athlete")
        coach_str = ""
        for coach in coachs:
            coach_str += coach.user_name + ","
        info["coach"] = coach_str[:-1]
        info["athlete_num"] = len(athletes)
        all_item.append(info)
    return render(request, 'admin_home.html', {
        "shoot_items": all_item
    })


def admin_coach(request):
    if request.method == 'POST':
        coach_name = request.POST['coach_name']
        gender = request.POST['gender']
        age = request.POST['age']
        coach_info = request.POST['coach_info']
        item_id = request.POST['item_id']
        password = request.POST['password']
        print(coach_name)
        coach = user_info(user_name=coach_name, gender=gender, age=age, intro=coach_info, item_id=item_id,
                          password=password, role="coach")
        coach.save()
    coachs = user_info.objects.filter(role="coach")
    all_cocahs = []
    for coach in coachs:
        c = {}
        items = shoot_items.objects.filter(id=coach.item_id)
        c["coach"] = coach
        if len(items) > 0:
            item = items[0]
            c["item_name"] = item.item_name
        else:
            c["item_name"] = ""
        all_cocahs.append(c)
    return render(request, 'admin_coach.html', {
        "coachs": all_cocahs
    })


def admin_sport(request):
    if request.method == 'POST':
        athlete_name = request.POST['athlete_name']
        gender = request.POST['gender']
        age = request.POST['age']
        athlete_info = request.POST['athlete_info']
        item_id = request.POST['item_id']
        password = request.POST['password']
        print(athlete_name)
        athlete = user_info(user_name=athlete_name, gender=gender, age=age, intro=athlete_info, item_id=item_id,
                            password=password, role="athlete")
        athlete.save()
    user_infos = user_info.objects.filter(role="athlete")
    all_athletes = []
    for athlete in user_infos:
        c = {}
        items = shoot_items.objects.filter(id=athlete.item_id)
        c["athlete"] = athlete
        if len(items) > 0:
            item = items[0]
            c["item_name"] = item.item_name
        else:
            c["item_name"] = ""
        all_athletes.append(c)
    return render(request, 'admin_sport.html', {
        'athletes': all_athletes
    })


def admin_analyse(request):
    return render(request, 'admin_analyse.html')


def admin_add_item(request):
    return render(request, 'admin_add_item.html')


def admin_delete_item(request):
    if request.method == 'GET':
        id = request.GET['id']
        users = user_info.objects.filter(item_id=int(id))
        if len(users) > 0:
            for user in users:
                user.item_id = None
                user.save()
        shoot_items.objects.get(id=id).delete()
    return redirect("admin_home")


def admin_modify_item(request):
    if request.method == 'GET':
        id = request.GET['id']
        shoot_item = shoot_items.objects.get(id=int(id))
        return render(request, 'admin_modify_item.html', {
            'shoot_item': shoot_item
        })
    if request.method == 'POST':
        id = request.POST['id']
        shoot_item = shoot_items.objects.get(id=int(id))
        shoot_item.item_name = request.POST['item_name']
        shoot_item.item_info = request.POST['item_info']
        shoot_item.item_rule = request.POST['item_rule']
        shoot_item.save()
        return redirect("admin_home")


def admin_add_coach(request):
    items = shoot_items.objects.all()
    return render(request, 'admin_add_coach.html', {
        "items": items
    })


def admin_delete_coach(request):
    if request.method == 'GET':
        id = request.GET['id']
        user_info.objects.get(id=id).delete()
    return redirect("admin_coach")


def admin_modify_coach(request):
    if request.method == 'GET':
        id = request.GET['id']
        coach = user_info.objects.get(id=int(id))
        items = shoot_items.objects.all()
        return render(request, 'admin_modify_coach.html', {
            'coach': coach,
            'items': items
        })
    if request.method == 'POST':
        id = request.POST['id']
        coach = user_info.objects.get(id=int(id))
        coach.user_name = request.POST['coach_name']
        coach.intro = request.POST['coach_info']
        coach.gender = request.POST['gender']
        coach.age = request.POST['age']
        coach.item_id = request.POST['item_id']
        coach.password = request.POST['password']
        coach.save()
        return redirect("admin_coach")


def admin_add_sport(request):
    items = shoot_items.objects.all()
    return render(request, 'admin_add_sport.html', {
        "items": items
    })


def admin_delete_sport(request):
    if request.method == 'GET':
        id = request.GET['id']
        user_info.objects.get(id=id).delete()
    return redirect("admin_sport")


def admin_modify_sport(request):
    if request.method == 'GET':
        id = request.GET['id']
        athlete = user_info.objects.get(id=int(id))
        items = shoot_items.objects.all()
        return render(request, 'admin_modify_sport.html', {
            'athlete': athlete,
            'items': items
        })
    if request.method == 'POST':
        id = request.POST['id']
        athlete = user_info.objects.get(id=int(id))
        athlete.user_name = request.POST['user_name']
        athlete.intro = request.POST['athlete_info']
        athlete.gender = request.POST['gender']
        athlete.age = request.POST['age']
        athlete.item_id = request.POST['item_id']
        athlete.password = request.POST['password']
        athlete.save()
        return redirect("admin_sport")


def test(request):
    return render(request, 'convert.html')


def coach(request):
    return render(request, 'coach.html')


def vue(request):
    return render(request, 'vue.html', {
        'message1': 'django'
    })
