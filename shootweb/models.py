from django.db import models
import django.utils.timezone as timezone


# Create your models here.
class ShootItems(models.Model):
    itemName = models.CharField(max_length=100, default="")
    itemInfo = models.TextField(null=True)
    itemRule = models.TextField(null=True)
    remark = models.TextField(null=True)


class UserInfo(models.Model):
    name = models.CharField(max_length=100, default="")
    userName = models.CharField(max_length=100, default="")
    password = models.CharField(max_length=100, default="")
    gender = models.CharField(max_length=10, null=True)   # 男/女
    age = models.IntegerField(null=True)
    role = models.CharField(max_length=100)   # admin, athlete, coach
    intro = models.TextField(null=True)
    remark = models.TextField(null=True)


class ItemCoachRelation(models.Model):
    coachId = models.IntegerField()
    itemId = models.IntegerField()
    remark = models.TextField(null=True)


class ItemAthleteRelation(models.Model):
    athleteId = models.IntegerField()
    itemId = models.IntegerField()
    remark = models.TextField(null=True)


class GameInfo(models.Model):
    gameName = models.CharField(max_length=100, default="")
    gameInfo = models.TextField(null=True)
    gameDate = models.CharField(max_length=100, default="")
    gameAddress = models.CharField(max_length=500, null=True)
    remark = models.TextField(null=True)


class ShakeBesideData(models.Model):
    gameId = models.IntegerField()
    athleteId = models.IntegerField()
    beside_x = models.DecimalField(max_digits=4, decimal_places=2)
    beside_y = models.DecimalField(max_digits=4, decimal_places=2)
    record_time = models.CharField(max_length=100,default="")
    date = models.CharField(max_length=100, default="")
    remark = models.TextField(null=True)


class ShakeUpData(models.Model):
    gameId = models.IntegerField()
    athleteId = models.IntegerField()
    up_data = models.DecimalField(max_digits=4, decimal_places=2)
    record_time = models.CharField(max_length=100, default="")
    date = models.CharField(max_length=100, default="")
    remark = models.TextField(null=True)


class HeartRateData(models.Model):
    athleteId = models.IntegerField()
    gameId = models.IntegerField()
    heartRate = models.IntegerField()
    date = models.CharField(max_length=100, default="")
    record_time = models.CharField(max_length=100, default="")
    remark = models.TextField(null=True)


class ShootData(models.Model):
    stageId = models.IntegerField()
    orderId = models.IntegerField()
    data = models.DecimalField(max_digits=4, decimal_places=2)
    rapid_time = models.DecimalField(max_digits=4, decimal_places=2)
    shoot_time = models.CharField(max_length=100, default="")
    record_time = models.CharField(max_length=100, default="")
    x_pos = models.DecimalField(max_digits=4, decimal_places=2)
    y_pos = models.DecimalField(max_digits=4, decimal_places=2)
    remark = models.TextField(null=True)


class StageInfo(models.Model):
    itemId = models.IntegerField()
    athleteId = models.IntegerField()
    gameId = models.IntegerField(null=True)
    target = models.CharField(max_length=100)
    totalGrade = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    stageTime = models.CharField(max_length=100, default="")
    remark = models.TextField(null=True)



# 记录每次抖动开始和结束的时间
class record_shake_time(models.Model):
    record_date = models.CharField(max_length=200)
    start_time = models.CharField(max_length=200)
    end_time = models.CharField(max_length=200)
    remark = models.TextField(null=True)

# 抖动数据
class shake_data(models.Model):
    report_id = models.IntegerField(default=0)
    record_id = models.IntegerField(default=0)
    shake_date = models.CharField(max_length=200)
    shake_time = models.CharField(max_length=200)
    x_data = models.TextField(null=True)
    y_data = models.TextField(null=True)
    remark = models.TextField(null=True)


# 记录每次心率开始和结束的时间
class record_heart_time(models.Model):
    record_date = models.CharField(max_length=200)
    start_time = models.CharField(max_length=200,default='')
    end_time = models.CharField(max_length=200,default='')
    remark = models.TextField(null=True)


# 心率数据
class heart_data(models.Model):
    report_id = models.IntegerField(default=0)
    record_id = models.IntegerField(default=0)
    heart_time = models.CharField(max_length=200)
    heart_date = models.CharField(max_length=200)
    heart_rate = models.CharField(max_length=200)
    average_rate = models.IntegerField(default=0)
    remark = models.TextField(null=True)

# 射击成绩
class shoot_grade(models.Model):
    report_id = models.IntegerField()
    grade_date = models.CharField(max_length=200)
    grade_time = models.CharField(max_length=200)
    grade = models.CharField(max_length=200)
    rapid_time = models.CharField(max_length=200)
    x_pos = models.CharField(max_length=200)
    y_pos = models.CharField(max_length=200)
    remark = models.TextField(null=True)

# 每五次射击的开始时间和结束时间
class shoot_report(models.Model):
    shoot_date = models.CharField(max_length=200)
    start_time = models.CharField(max_length=200)
    end_time = models.CharField(max_length=200)
    remark = models.TextField(null=True)


