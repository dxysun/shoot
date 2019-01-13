from django.shortcuts import render
from shootweb.models import *
from django.http.response import JsonResponse
from . import shootlib
from . import watch_grade_file
from django.shortcuts import redirect
import json

observer = None


# Create your views here.
def index(request):
    return render(request, 'main.html')


def login_admin(request):
    if request.method == 'GET':
        return render(request, 'login_admin.html')
    result = {}
    if request.method == "POST":
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
        result = dict()
        result['data'] = []
        for user in users:
            u = dict()
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
        request.session['user'] = user.user_name
        request.session['user_id'] = user.id
        request.session['role'] = user.role
        print("observer get")
        global observer
        if observer is not None:
            print("observer not none")
            observer.stop()
            del observer
        observer = watch_grade_file.start_watch(user.user_name)
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
    user_name = request.session.get('user')
    shoot_reports = shoot_report.objects.filter(user_name=user_name)
    stage_four = {}
    stage_six = {}
    stage_eight = {}
    for report in shoot_reports:
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
        for grade in shoot_grades:
            if stage == 4:
                heart_four += grade.heart_rate
                stage_four = shootlib.set_report_shoot_rapid_info(stage_four, grade.grade, grade.rapid_time, i, stage)
            if stage == 6:
                heart_six += grade.heart_rate
                stage_six = shootlib.set_report_shoot_rapid_info(stage_six, grade.grade, grade.rapid_time, i, stage)
            if stage == 8:
                heart_eight += grade.heart_rate
                stage_eight = shootlib.set_report_shoot_rapid_info(stage_eight, grade.grade, grade.rapid_time, i, stage)
            i += 1

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
    return render(request, 'sport_home.html', {
        'stage_four': stage_four,
        'stage_six': stage_six,
        'stage_eight': stage_eight
    })


def coach_home(request):
    return render(request, 'coach_home.html')


def coach_sport_info(request):
    return render(request, 'coach_sport_info.html')


def coach_game_info(request):
    return render(request, 'coach_game_info.html')


def coach_sport_info_detail(request):
    return render(request, 'coach_sport_info_detail.html')


def sport_game_analyse(request):
    user_name = request.session.get('user', "")
    shoot_reports = []
    best_grade = 0
    bad_grade = 100
    total_grade = 0
    report_num = 0
    average_grade = 0
    quadrant = [0, 0, 0, 0]
    right_up = 0
    left_up = 0
    left_blow = 0
    right_blow = 0
    grades = []
    r_pos = []
    p_pos = []
    x_pos = []
    y_pos = []
    hearts = []
    report_shake_info = []
    if request.method == 'POST':
        report_id = request.POST['report_id']
        ids = report_id.split(",")
        for id in ids:
            # print(id)
            report_num += 1
            report = shoot_report.objects.get(id=id)
            grade = float(report.total_grade)
            grades.append(grade)
            total_grade += grade
            if grade > best_grade:
                best_grade = grade
            if grade < bad_grade:
                bad_grade = grade
            shoot_reports.append(report)

            shake_info = {}
            shoot_grades = shoot_grade.objects.filter(report_id=id).order_by('grade_detail_time')
            heart_temp = []
            heart_total = 0
            shake_info['x_pos'] = []
            shake_info['y_pos'] = []
            shake_info['grades'] = []
            for grade in shoot_grades:
                # print(grade.id)
                shake_info['grades'].append(grade.grade)
                x = float(grade.x_pos)
                y = float(grade.y_pos)
                x_pos.append(x)
                shake_info['x_pos'].append(x)
                shake_info['y_pos'].append(y)
                y_pos.append(y)
                r, p = shootlib.cart_to_polar(x, y)
                r = 11 - r
                r_pos.append(r)
                p_pos.append(p)
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
                if grade.heart_rate is not None and grade.heart_rate != 0:
                    heart_temp.append(grade.heart_rate)
                    heart_total += grade.heart_rate
            if len(heart_temp) != 0:
                heart = heart_total / len(heart_temp)
            else:
                heart = 0
            hearts.append(heart)
            if report.x_shake_pos is not None and report.x_up_shake_pos is not None:
                y_shake_pos = report.y_shake_pos.split(",")
                x_up_shake_pos = report.x_up_shake_pos.split(",")
                y_up_shake_pos = report.y_up_shake_pos.split(",")
                y_shake_data = shootlib.process_shake_pos_info(y_shake_pos)
                x_up_shake_data = shootlib.process_shake_pos_info(x_up_shake_pos)
                y_up_shake_data = shootlib.process_shake_pos_info(y_up_shake_pos)
                is_insert = False
                y_data = y_shake_data.split(",")
                x_up_data = x_up_shake_data.split(",")
                y_up_data = y_up_shake_data.split(",")

                y_data = shootlib.get_int_data(y_data, is_negative=True)
                x_up_data = shootlib.get_int_data(x_up_data)
                y_up_data = shootlib.get_int_data(y_up_data)

                y_data, num = shootlib.cut_shake_data(y_data)
                x_up_data = x_up_data[num:]
                y_up_data = y_up_data[num:]

                y_data_plus = shootlib.shake_data_process(y_data)
                x_up_data_plus = shootlib.shake_data_process(x_up_data)

                nums = shootlib.get_shoot_point(y_data, is_insert=is_insert)
                up_nums = shootlib.get_shoot_point(y_up_data, is_insert=is_insert, limit=5)

                y_shoot_pos, y_pos_array = shootlib.shake_get_plus_shoot_point(y_data_plus, nums, is_insert=is_insert)
                x_shoot_pos, x_pos_array = shootlib.shake_get_plus_shoot_point(x_up_data_plus, nums,
                                                                               is_insert=is_insert)
                x_up_shoot_pos, _ = shootlib.shake_get_plus_shoot_point(x_up_data_plus, up_nums, is_insert=is_insert)
                up_x_10_pos, up_shake_rate = shootlib.get_up_shoot_limit(x_up_shoot_pos, shake_info['x_pos'],
                                                                         shake_info['grades'])

                shake_info['y_data_plus'] = y_data_plus
                shake_info['x_up_data_plus'] = x_up_data_plus
                shake_info['x_shoot_pos'] = x_shoot_pos
                shake_info['y_shoot_pos'] = y_shoot_pos
                shake_info['up_shake_rate'] = up_shake_rate
            report_shake_info.append(shake_info)
        average_grade = round(total_grade / report_num, 2)
    # average_in_circle = shootlib.get_average_in_circle(x_pos, y_pos)
    # print(average_in_circle)
    grade_stability = shootlib.get_grade_stability(x_pos, y_pos)
    grade_info = dict(grades=grades, r_pos=r_pos, p_pos=p_pos, hearts=hearts, grade_stability=grade_stability)
    return render(request, 'sport_game_analyse.html', {
        'shoot_reports': shoot_reports,
        'grade_info': json.dumps(grade_info),
        'report_shake_info': json.dumps(report_shake_info),
        'best_grade': best_grade,
        'bad_grade': bad_grade,
        'average_grade': average_grade,
        'right_up': right_up,
        'left_up': left_up,
        'left_blow': left_blow,
        'right_blow': right_blow,
    })


def sport_game_analyse_id(request):
    report_id = request.GET['id']
    report = shoot_report.objects.get(id=report_id)
    grades = []
    hearts = []
    r_pos = []
    p_pos = []
    x_pos = []
    y_pos = []
    shoot_grades = shoot_grade.objects.filter(report_id=report_id).order_by('grade_detail_time')
    rapid_data = []
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
        hearts.append(grade.heart_rate)
    grade_stability = shootlib.get_grade_stability(x_pos, y_pos)
    grade_info = dict(r_pos=r_pos, p_pos=p_pos, x_pos=x_pos, y_pos=y_pos, grades=grades, hearts=hearts,
                      rapid_data=rapid_data, grade_stability=grade_stability)
    stage = int(report.remark)
    shake_info = {}
    five_pos_info = {}
    x_data_pos = report.x_shake_pos
    y_data_pos = report.y_shake_pos
    x_up_data_pos = report.x_up_shake_pos
    y_up_data_pos = report.y_up_shake_pos
    x_shake_data = report.x_shake_data
    y_shake_data = report.y_shake_data
    x_up_shake_data = report.x_up_shake_data
    y_up_shake_data = report.y_up_shake_data

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
        up_nums, x_shoot_array = shootlib.get_shoot_point(y_up_data, is_insert=is_insert, limit=5, stage = stage)
        # print(nums)
        # print(up_nums)

        if is_insert:
            x_data, y_data = shootlib.insert(x_data, y_data)
            x_up_data, y_up_data = shootlib.insert(x_up_data, y_up_data)

        x_data_plus = shootlib.shake_data_process(x_data)
        y_data_plus = shootlib.shake_data_process(y_data)
        x_up_data_plus = shootlib.shake_data_process(x_up_data)
        y_up_data_plus = shootlib.shake_data_process(y_up_data, is_negative=True)

        y_shoot_pos, y_pos_array = shootlib.shake_get_plus_shoot_point(y_data_plus, nums, is_insert, pos_num,
                                                                       after_shoot)
        x_shoot_pos, x_pos_array = shootlib.shake_get_plus_shoot_point(x_up_data_plus, nums, is_insert, pos_num,
                                                                       after_shoot)
        # print(x_pos_array)
        # print(y_pos_array)

        x_up_shoot_pos, _ = shootlib.shake_get_plus_shoot_point(x_up_data_plus, up_nums, is_insert, pos_num,
                                                                after_shoot)
        y_up_shoot_pos, _ = shootlib.shake_get_plus_shoot_point(y_up_data_plus, up_nums, is_insert, pos_num,
                                                                after_shoot)

        y_stability_array = shootlib.shake_get_stability_shoot_array(y_pos_array, after_shoot, is_insert=is_insert)

        up_x_10_pos, up_shake_rate = shootlib.get_up_shoot_limit(x_up_shoot_pos, x_pos, grades)
        # print(x_up_shoot_pos)
        # print(up_x_10_pos)
        y_shoot_pos_new = y_shoot_pos.copy()
        if up_shake_rate is not None and len(y_shoot_pos_new) == 5:
            y_data_plus, y_shoot_pos_new = shootlib.process_shoot_y_pos_to_one_line(y_data_plus, y_shoot_array,
                                                                                    up_shake_rate, y_shoot_pos_new,
                                                                                    y_pos)

            x_pos_str, x_shoot_point = shootlib.process_pos_array(x_pos_array, x_shoot_pos, x_pos, up_shake_rate)
            y_pos_str, y_shoot_point = shootlib.process_pos_array(y_pos_array, y_shoot_pos, y_pos, up_shake_rate)

            five_pos_info['up_shake_rate'] = up_shake_rate
            five_pos_info['x_pos_str'] = x_pos_str
            five_pos_info['y_pos_str'] = y_pos_str
            five_pos_info['y_stability_array'] = y_stability_array
            five_pos_info['x_shoot_point'] = x_shoot_point
            five_pos_info['y_shoot_point'] = y_shoot_point

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
        'grade_info': json.dumps(grade_info),
        'shake_info': json.dumps(shake_info),
        'five_pos_info': json.dumps(five_pos_info),
        'shoot_info': shoot_grades,
        'beside_y_nums': nums,
    })


def sport_game_history(request):
    user_name = request.session.get('user', "")
    shootlib.update_data(user_name)
    shoot_dates = shootlib.get_shoot_date(user_name)
    if request.method == 'GET':
        report = shoot_report.objects.filter(user_name=user_name).last()
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
        shoot_reports = shoot_report.objects.filter(user_name=user_name).filter(shoot_date=date1).order_by('shoot_time')
        all_report = shootlib.split_report(shoot_reports)
        return render(request, 'sport_game_history.html', {
            'shoot_reports': shoot_reports,
            'all_report': all_report,
            'shoot_dates': shoot_dates,
            'date1': date1,
            'date2': date2
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
        athlete.item_id = None
        if request.POST['item_id'] is not None:
            athlete.item_id = request.POST['item_id']
        athlete.password = request.POST['password']
        athlete.save()
        return redirect("admin_sport")


def test(request):
    return render(request, 'test.html')


def coach(request):
    return render(request, 'coach.html')


def vue(request):
    return render(request, 'vue.html', {
        'message1': 'django'
    })
