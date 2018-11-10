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
    url('^login$', views.login, name="login"),
    url('^login_admin$', views.login_admin, name="login_admin"),
    url('^logout', views.logout, name="logout"),
    url('^get_user_info$', views.get_user_info, name="get_user_info"),
    url('^register', views.register, name="register"),
    url('^update_data', views.update_data, name="update_data"),
    url('^sport/home', views.sport_home, name="sport_home"),
    url('^sport/game_analyse$', views.sport_game_analyse, name="sport_game_analyse"),
    url('^sport/game_analyse_id$', views.sport_game_analyse_id, name="sport_game_analyse_id"),
    url('^sport/game_history', views.sport_game_history, name="sport_game_history"),
    url('^coach/home$', views.coach_home, name="coach_home"),
    url('^coach/sport_info$', views.coach_sport_info, name="coach_sport_info"),
    url('^coach/game_info$', views.coach_game_info, name="coach_game_info"),
    url('^coach/sport_info_detail$', views.coach_sport_info_detail, name="coach_sport_info_detail"),
    url('^admin/home$', views.admin_home, name="admin_home"),
    url('^admin/item/add', views.admin_add_item, name="admin_add_item"),
    url('^admin/item/delete', views.admin_delete_item, name="admin_delete_item"),
    url('^admin/item/modify', views.admin_modify_item, name="admin_modify_item"),
    url('^admin/coach$', views.admin_coach, name="admin_coach"),
    url('^admin/coach/add', views.admin_add_coach, name="admin_add_coach"),
    url('^admin/coach/delete', views.admin_delete_coach, name="admin_delete_coach"),
    url('^admin/coach/modify', views.admin_modify_coach, name="admin_modify_coach"),
    url('^admin/sport$', views.admin_sport, name="admin_sport"),
    url('^admin/sport/add', views.admin_add_sport, name="admin_add_sport"),
    url('^admin/sport/delete', views.admin_delete_sport, name="admin_delete_sport"),
    url('^admin/sport/modify', views.admin_modify_sport, name="admin_modify_sport")
]
