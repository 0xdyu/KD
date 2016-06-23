# coding:utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Order(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    weight = models.FloatField(null=True,blank=True,verbose_name=u"重量")
    shipping_user_id = models.CharField(null=True, max_length=50, verbose_name=u"寄送人邮箱")
    sender_id = models.CharField(null=True, max_length=10, verbose_name=u"发件人")
    receiver_id = models.CharField(null=True,max_length=10, verbose_name=u"收件人")

    def __unicode__(self):
        return self.id

class OrderStatus(models.Model):
    order_id = models.CharField(max_length=10, verbose_name=u"订单号")
    time = models.DateTimeField(auto_now_add=True,verbose_name=u"时间")
    status = models.CharField(max_length=50,verbose_name=u"状态")
    location = models.CharField(max_length=50,verbose_name=u"当前位置")
    primKey= models.CharField(max_length=50, primary_key=True)
    def __unicode__(self):
        return self.order_id

class EndUser(models.Model):
    user_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50,verbose_name=u"姓名")
    phone_number = models.CharField(max_length=50,verbose_name=u"联系方式")
    company_name = models.CharField(max_length=50,verbose_name=u"公司名")
    address = models.CharField(null=True, max_length=50,verbose_name=u"地址")
    postcode = models.CharField(max_length=50,verbose_name=u"邮政编码")
    def __unicode__(self):
        return self.user_id

class ShippingUser(models.Model):
    user_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50,verbose_name=u"姓名")
    phone_number = models.CharField(max_length=50,verbose_name=u"联系方式")
    company_name = models.CharField(max_length=50,verbose_name=u"公司名")
    address = models.CharField(null=True, max_length=50,verbose_name=u"地址")
    postcode = models.CharField(max_length=50,verbose_name=u"邮政编码")
    def __unicode__(self):
        return self.user_id
