from django.shortcuts import render


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
    return render(request, 'sport_game_analyse.html')


def sport_game_history(request):
    return render(request, 'sport_game_history.html')


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
