# -*- coding:utf-8 -*- 
__author__ = 'dxy'
import sys
import os
import pandas as pd
import time
import datetime
import math
from scipy.interpolate import interp1d
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
import model_evaluation_utils as meu
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import FeatureUnion
from sklearn.tree import DecisionTreeRegressor

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def get_shoot_area(x, y):
    x = float(x)
    y = float(y)
    if x > 0 and y > 0:
        return 1
    elif x < 0 and y > 0:
        return 2
    elif x < 0 and y < 0:
        return 3
    else:
        return 4


def add_shoot_area():
    grade_first_shoot_info_4_with_feature = pd.read_excel('data/grade_first_shoot_info_4_with_feature.xlsx')
    grade_first_shoot_info_6_with_feature = pd.read_excel('data/grade_first_shoot_info_6_with_feature.xlsx')
    grade_first_shoot_info_8_with_feature = pd.read_excel('data/grade_first_shoot_info_8_with_feature.xlsx')
    grade_first_shoot_info_8_with_feature['shoot_area'] = grade_first_shoot_info_8_with_feature.apply(
        lambda x: get_shoot_area(x.x_pos, x.y_pos), axis=1)
    grade_first_shoot_info_4_with_feature['shoot_area'] = grade_first_shoot_info_4_with_feature.apply(
        lambda x: get_shoot_area(x.x_pos, x.y_pos), axis=1)
    grade_first_shoot_info_6_with_feature['shoot_area'] = grade_first_shoot_info_6_with_feature.apply(
        lambda x: get_shoot_area(x.x_pos, x.y_pos), axis=1)
    grade_first_shoot_info_8_with_feature.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_8_with_feature.xlsx")
    grade_first_shoot_info_6_with_feature.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_6_with_feature.xlsx")
    grade_first_shoot_info_4_with_feature.to_excel(
        "D:/workSpace/PythonWorkspace/shoot/shootweb/data/grade_first_shoot_info_4_with_feature.xlsx")


def one_hot_test(train_set):
    shoot_area_encoded = train_set['shoot_area'].values
    encoder = OneHotEncoder()
    shoot_area_1hot = encoder.fit_transform(shoot_area_encoded.reshape(-1, 1))
    shoot_area_1hot.toarray()


def get_feature_label(train_df, feature_col, label_name):
    shoot_features = train_df[feature_col]  # 最后一列是目标变量
    shoot_class_labels = np.array(train_df[label_name])
    return shoot_features, shoot_class_labels


def normalize(train_X):
    shoot_ss = StandardScaler().fit(train_X)
    return shoot_ss


def train_model_predict(shoot_train_SX, shoot_train_y, shoot_test_SX, shoot_test_y, shoot_label_names):
    shoot_rf = RandomForestClassifier()
    shoot_rf.fit(shoot_train_SX, shoot_train_y)

    shoot_rf_predictions = shoot_rf.predict(shoot_test_SX)
    meu.display_model_performance_metrics(true_labels=shoot_test_y, predicted_labels=shoot_rf_predictions,
                                          classes=shoot_label_names)
    return shoot_rf


def display_importance(shoot_rf, shoot_feature_names):
    shoot_rf_feature_importances = shoot_rf.feature_importances_
    shoot_rf_feature_names, shoot_rf_feature_scores = zip(
        *sorted(zip(shoot_feature_names, shoot_rf_feature_importances),
                key=lambda x: x[1]))
    y_position = list(range(len(shoot_rf_feature_names)))
    plt.barh(y_position, shoot_rf_feature_scores, height=0.6, align='center')
    plt.yticks(y_position, shoot_rf_feature_names)
    plt.xlabel(u'重要性得分')
    plt.ylabel(u'特征')
    t = plt.title(u'随机森林特征重要性')
    plt.show()


def train_first_shoot_8_data(grade_first_shoot_info_8_with_feature):
    # grade_first_shoot_info_8_with_feature = pd.read_excel('data/grade_first_shoot_info_8_with_feature.xlsx')
    train_8_first_df = grade_first_shoot_info_8_with_feature[
        ['rapid_time', 'shoot_area', 'heart_rate', 'x_average', 'y_stability', 'grade']]
    feature_col = ['rapid_time', 'shoot_area', 'heart_rate', 'x_average', 'y_stability']
    label_col = ['grade']
    shoot_features, shoot_class_labels = get_feature_label(train_8_first_df, feature_col, label_col)
    shoot_train_X, shoot_test_X, shoot_train_y, shoot_test_y = train_test_split(shoot_features, shoot_class_labels,
                                                                                test_size=0.3, random_state=42)
    shoot_ss = normalize(shoot_train_X)
    shoot_train_SX = shoot_ss.transform(shoot_train_X)

    shoot_test_SX = shoot_ss.transform(shoot_test_X)

    shoot_label_names = [10, 9]
    shoot_rf = train_model_predict(shoot_train_SX, shoot_train_y, shoot_test_SX, shoot_test_y, shoot_label_names)
    display_importance(shoot_rf, feature_col)


class DataFrameSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names):
        self.attribute_names = attribute_names

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.attribute_names].values


def use_pipeline(num_attribs, cat_attribs=None):
    # num_attribs = ['rapid_time', 'heart_rate', 'x_average', 'y_stability']
    # cat_attribs = ["shoot_area"]
    num_pipeline = Pipeline([
        ('selector', DataFrameSelector(num_attribs)),
        ('std_scaler', StandardScaler())
    ])
    if cat_attribs is not None:
        cat_pipeline = Pipeline([
            ('selector', DataFrameSelector(cat_attribs)),
            ('label_binarizer', OneHotEncoder())
        ])

        full_pipeline = FeatureUnion(transformer_list=[
            ("num_pipeline", num_pipeline),
            ("cat_pipeline", cat_pipeline)
        ])
        return full_pipeline
    else:
        return num_pipeline


def train_data_and_predict(all_data_df, feature_names, label_name):
    feature = all_data_df[feature_names].copy()
    shoot_labels = all_data_df[label_name].copy()
    train_x, test_x, train_y, test_y = train_test_split(feature, shoot_labels, test_size=0.3, random_state=42)
    #
    # full_pipeline = use_pipeline(feature_names)
    #
    # train_x_prepared = full_pipeline.fit_transform(train_x)
    # test_x_prepared = full_pipeline.transform(test_x)

    # shoot_reg = DecisionTreeRegressor()
    shoot_reg = RandomForestClassifier()
    shoot_reg.fit(train_x, train_y)

    shoot_dt_predictions = shoot_reg.predict(test_x)
    label_class = list(set(shoot_labels.values))
    meu.display_model_performance_metrics(true_labels=test_y, predicted_labels=shoot_dt_predictions,
                                          classes=label_class)

    # shoot_feature_names = ['rapid_time', 'heart_rate', 'x_average', 'y_stability', 'shoot_area1', 'shoot_area2',
    #                        'shoot_area3', 'shoot_area4']
    display_importance(shoot_reg, feature_names)


if __name__ == "__main__":
    print()
    # add_shoot_area()
    grade_first_shoot_info_8_with_feature = pd.read_excel('data/grade_first_shoot_info_8_with_feature.xlsx')
    grade_first_shoot_info_4_with_feature = pd.read_excel('data/grade_first_shoot_info_4_with_feature.xlsx')
    grade_first_shoot_info_6_with_feature = pd.read_excel('data/grade_first_shoot_info_6_with_feature.xlsx')
    # train_first_shoot_8_data(grade_first_shoot_info_4_with_feature)
    shoot_feature_names = ['rapid_time', 'heart_rate', 'y_stability']
    shoot_label_names = 'grade'
    train_data_and_predict(grade_first_shoot_info_4_with_feature, shoot_feature_names, shoot_label_names)
