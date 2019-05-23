# -*- coding:utf-8 -*- 
__author__ = 'dxy'
import numpy as np
from sklearn.model_selection import KFold
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin, clone
from sklearn import metrics
from sklearn.externals import joblib
import os

dirname, filename = os.path.split(os.path.abspath(__file__))
pre_path = os.path.abspath(os.path.dirname(dirname))
print("stack_pre_path:" + pre_path)


class StackingAveragedModels(BaseEstimator, RegressorMixin, TransformerMixin):
    def __init__(self, base_models, meta_model, n_folds=5):
        self.base_models = base_models
        self.meta_model = meta_model
        self.n_folds = n_folds

    # 我们将原来的模型clone出来，并且进行实现fit功能
    def fit(self, X, y):
        self.base_models_ = [list() for x in self.base_models]
        self.meta_model_ = clone(self.meta_model)
        kfold = KFold(n_splits=self.n_folds, shuffle=True, random_state=156)

        # 对于每个模型，使用交叉验证的方法来训练初级学习器，并且得到次级训练集
        out_of_fold_predictions = np.zeros((X.shape[0], len(self.base_models)))
        self.importance_array = []
        self.accuracy_array = []
        feature_len = X.shape[1]
        for i, model in enumerate(self.base_models):
            model_fea_importance = None
            accuracy_data = 0
            for train_index, holdout_index in kfold.split(X, y):
                instance = clone(model)
                self.base_models_[i].append(instance)
                instance.fit(X[train_index], y[train_index])
                if model_fea_importance is None:
                    model_fea_importance = instance.feature_importances_.copy()
                else:
                    for k in range(feature_len):
                        model_fea_importance[k] += instance.feature_importances_[k]
                y_pred = instance.predict(X[holdout_index])
                accuracy_data += metrics.accuracy_score(y[holdout_index], y_pred)
                out_of_fold_predictions[holdout_index, i] = y_pred
            for k in range(feature_len):
                model_fea_importance[k] = model_fea_importance[k] / self.n_folds
            self.importance_array.append(model_fea_importance)
            self.accuracy_array.append(accuracy_data / self.n_folds)

        # 使用次级训练集来训练次级学习器
        self.meta_model_.fit(out_of_fold_predictions, y)
        return self

    # 在上面的fit方法当中，我们已经将我们训练出来的初级学习器和次级学习器保存下来了
    # predict的时候只需要用这些学习器构造我们的次级预测数据集并且进行预测就可以了
    def predict(self, X):
        meta_features = np.column_stack([
            np.column_stack([model.predict(X) for model in base_models]).mean(axis=1)
            for base_models in self.base_models_])
        return self.meta_model_.predict(meta_features)

    def get_importance_feature(self):
        sum_accuracy = sum(self.accuracy_array)
        accuracy_per = []
        for accuracy in self.accuracy_array:
            accuracy_per.append(accuracy / sum_accuracy)
        feature_array = [0] * len(self.importance_array[0])
        for i in range(len(self.importance_array)):
            sum_fea = sum(self.importance_array[i])
            k = 0
            for f in self.importance_array[i]:
                feature_array[k] = round(feature_array[k] + ((f / sum_fea) * 100 * accuracy_per[i]), 2)
                k += 1
        return feature_array

    def save_model(self, user_name):
        i = 0
        for base_model in self.base_models_:
            joblib.dump(base_model, pre_path + '/shootweb/data/' + user_name + '_model_' + str(i) + '.pkl')
            i += 1
        self.meta_model_.save_model(user_name)


class NetDnnClassifier(BaseEstimator, RegressorMixin, TransformerMixin):
    def __init__(self, input_shape=None):
        from keras.models import Sequential
        from keras.layers import Dense
        if input_shape is None:
            input_shape = 5
        self.wtp_dnn_model = Sequential()
        self.wtp_dnn_model.add(Dense(16, activation='relu', input_shape=(input_shape,)))  # 输入层11个节点对应11个特征
        self.wtp_dnn_model.add(Dense(16, activation='relu'))
        self.wtp_dnn_model.add(Dense(16, activation='relu'))
        self.wtp_dnn_model.add(Dense(1, activation='sigmoid'))
        self.wtp_dnn_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    def fit(self, tarin_X, train_y):
        history = self.wtp_dnn_model.fit(tarin_X, train_y, epochs=10, batch_size=5, shuffle=True, validation_split=0.1,
                                         verbose=1)

    def predict(self, test_x):
        return self.wtp_dnn_model.predict_classes(test_x)

    def save_model(self, user_name):
        self.wtp_dnn_model.save(pre_path + '/shootweb/data/dnn_' + user_name + '.h5')
