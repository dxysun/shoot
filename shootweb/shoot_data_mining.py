import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import django
import datetime
import json
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
import model_evaluation_utils as meu
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
import shootlib

dirname, filename = os.path.split(os.path.abspath(__file__))
pre_path = os.path.abspath(os.path.dirname(dirname))
sys.path.append(pre_path + '/shoot')
os.chdir(pre_path + '/shoot')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot.settings")
django.setup()
from shootweb.models import *

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def train_save_model():
    grade_four_shoot_info_4_with_feature = pd.read_excel('../shootweb/data/grade_four_shoot_info_4_with_feature.xlsx')
    grade_four_shoot_info_6_with_feature = pd.read_excel('../shootweb/data/grade_four_shoot_info_6_with_feature.xlsx')
    grade_four_shoot_info_8_with_feature = pd.read_excel('../shootweb/data/grade_four_shoot_info_8_with_feature.xlsx')
    all_shoot_info = grade_four_shoot_info_8_with_feature.append(grade_four_shoot_info_6_with_feature)
    all_shoot_info = all_shoot_info.append(grade_four_shoot_info_4_with_feature)
    all_shoot_info['label'] = all_shoot_info['grade'].apply(lambda value: 1 if value == 10 else 0)

    all_shoot_info = all_shoot_info[all_shoot_info['move_distance'] > 60]
    all_feature_names = ['x_pos', 'y_pos', 'heart_rate', 'y_stability', 'x_average']
    all_label_name = 'label'

    all_shoot_features = all_shoot_info[all_feature_names].copy()
    all_shoot_labels = all_shoot_info[all_label_name].copy()
    train_x_all, test_x_all, train_y_all, test_y_all = train_test_split(all_shoot_features, all_shoot_labels,
                                                                        test_size=0.3, random_state=42)
    shoot_reg_all = RandomForestClassifier()
    shoot_reg_all.fit(train_x_all, train_y_all)

    shoot_dt_predictions_all = shoot_reg_all.predict(test_x_all)
    label_class_all = list(set(all_shoot_labels.values))
    meu.display_model_performance_metrics(true_labels=test_y_all, predicted_labels=shoot_dt_predictions_all,
                                          classes=label_class_all)
    joblib.dump(shoot_reg_all, '../shootweb/data/shoot_reg_all.pkl')
    return show_importance(shoot_reg_all, all_feature_names)
    # clf = joblib.load('data/shoot_reg_all.pkl')
    # test_data = test_x_all.iloc[3].values.reshape(1, -1)
    # print(clf.predict(test_data))


def show_importance(shoot_dt, shoot_feature_names):
    shoot_dt_feature_importances = shoot_dt.feature_importances_
    res = {}
    for shoot_dt_feature_names, shoot_dt_feature_scores in zip(shoot_feature_names, shoot_dt_feature_importances):
        res[shoot_dt_feature_names] = shoot_dt_feature_scores
    return res


def save_model_to_sql():
    r = train_save_model()
    print(r)
    d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_model = user_model_info(user_name="A", model_path="data/shoot_reg_all.pkl", build_time=d, model_type=0,
                                 model_info=json.dumps(r))
    user_model.save()


def predict_grade():
    user_model = user_model_info.objects.filter(user_name="A")
    clf = joblib.load('../shootweb/' + user_model[0].model_path)

    shoot_reports = shoot_report.objects.all()

    for report in shoot_reports:
        print(report.shoot_date + " " + report.start_time)
        stage = int(report.remark)
        # print(report.y_shake_pos)
        # print(report.x_up_shake_data)
        y_data_pos = report.y_shake_pos.split(",")
        x_up_data_pos = report.x_up_shake_pos.split(",")
        y_up_data_pos = report.y_up_shake_pos.split(",")

        y_up_shake_data = shootlib.process_shake_pos_info(y_up_data_pos)
        y_shake_data = shootlib.process_shake_pos_info(y_data_pos)
        x_up_shake_data = shootlib.process_shake_pos_info(x_up_data_pos)

        y_up_data = y_up_shake_data.split(",")
        y_data = y_shake_data.split(",")
        x_up_data = x_up_shake_data.split(",")
        y_data = shootlib.get_int_data(y_data, is_negative=True)
        x_up_data = shootlib.get_int_data(x_up_data)
        y_up_data = shootlib.get_int_data(y_up_data)

        y_data, num = shootlib.cut_shake_data(y_data)
        x_up_data = x_up_data[num:]
        y_up_data = y_up_data[num:]

        if stage == 4:
            pos_num = 8
        elif stage == 6:
            pos_num = 10
        else:
            pos_num = 15
        after_shoot = 1
        nums, y_shoot_array = shootlib.get_shoot_point(y_data, stage=stage)
        # up_nums, x_shoot_array = shootlib.get_shoot_point(y_up_data, limit=5)
        y_data_plus = shootlib.shake_data_process(y_data)
        x_up_data_plus = shootlib.shake_data_process(x_up_data)
        y_shoot_pos, y_pos_array = shootlib.shake_get_plus_shoot_point(y_data_plus, nums, pos_num=pos_num,
                                                                       after_shoot=after_shoot)
        x_shoot_pos, x_pos_array = shootlib.shake_get_plus_shoot_point(x_up_data_plus, nums, pos_num=pos_num,
                                                                       after_shoot=after_shoot)

        x_average_array, move_distance = shootlib.shake_get_average_x_shoot_array(x_pos_array, after_shoot,
                                                                                  is_insert=False,
                                                                                  get_distance=True)
        y_stability_array = shootlib.shake_get_stability_shoot_array(y_pos_array, after_shoot)

        shoot_grades = shoot_grade.objects.filter(report_id=report.id).order_by('grade_detail_time')
        first_grade = shoot_grades[0]
        last_x_pos = float(first_grade.x_pos)
        last_rapid_time = float(first_grade.rapid_time)
        for i in range(1, len(shoot_grades)):
            grade = shoot_grades[i]
            diff_pos = (last_x_pos - float(grade.x_pos) + i * 750)
            diff_rapid = float(grade.rapid_time) - last_rapid_time
            if i == 4 and float(grade.rapid_time) < 1:
                diff_rapid = float(grade.rapid_time) + stage - last_rapid_time
            if diff_rapid < 0:
                print(i)
                print("diff_rapid:" + str(diff_rapid))

            last_x_pos = float(grade.x_pos)
            last_rapid_time = float(grade.rapid_time)
            # all_feature_names = ['x_pos', 'y_pos', 'heart_rate', 'y_stability', 'x_average']
            if len(y_stability_array) == 5 and len(x_average_array) == 5:
                a = np.array([float(first_grade.x_pos), float(first_grade.y_pos), int(first_grade.heart_rate),
                              y_stability_array[i], x_average_array[i]]).reshape(1, -1)
                print(clf.predict(a))
                if clf.predict(a) == 1:
                    grade.remark = 10
                else:
                    grade.remark = 9
                grade.save()


if __name__ == "__main__":
    print()
    # predict_grade()

