# -*- coding:utf-8 -*- 
__author__ = 'dxy'
from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name="index"),
    url('^test$', views.test, name="test"),
    url('^main$', views.main, name="main"),
    url('^coach$', views.coach, name="coach"),
    url('^vue', views.vue, name="vue"),

    url('^login', views.login, name="login"),
    url('^register', views.register, name="register"),
    url('^sport/home', views.sport_home, name="sport_home"),
    url('^sport/game_analyse', views.sport_game_analyse, name="sport_game_analyse"),
    url('^sport/game_history', views.sport_game_history, name="sport_game_history"),
    url('^coach/home', views.coach_home, name="coach_home"),
    url('^coach/sport_info$', views.coach_sport_info, name="coach_sport_info"),
    url('^coach/game_info$', views.coach_game_info, name="coach_game_info"),
    url('^coach/sport_info_detail$', views.coach_sport_info_detail, name="coach_sport_info_detail"),
    url('^admin/home', views.admin_home, name="admin_home"),
    url('^admin/coach', views.admin_coach, name="admin_coach"),
    url('^admin/sport', views.admin_sport, name="admin_sport"),
    url('^admin/add_item', views.admin_add_item, name="admin_add_item"),
    url('^admin/add_coach', views.admin_add_coach, name="admin_add_coach"),
    url('^admin/add_sport', views.admin_add_sport, name="admin_add_sport")
]
