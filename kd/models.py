# coding:utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class EndUser(models.Model):
    user_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50,verbose_name=u"姓名")
    phone_number = models.CharField(max_length=50,verbose_name=u"联系方式")
    company_name = models.CharField(null=True,blank=True,max_length=50,verbose_name=u"公司名")
    address = models.CharField(null=True, max_length=50,verbose_name=u"地址")
    postcode = models.CharField(max_length=50,verbose_name=u"邮政编码")
    def __unicode__(self):
        return self.user_id

class Order(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    weight = models.FloatField(null=True,blank=True,verbose_name=u"重量")
    shipping_user_id = models.CharField(null=True, max_length=50, verbose_name=u"寄送人邮箱")
    #sender_id = models.CharField(null=True, max_length=10, verbose_name=u"发件人")
    sender = models.ForeignKey(EndUser, on_delete=models.CASCADE, verbose_name=u"发件人", related_name="sender_instance")
    #receiver_id = models.CharField(null=True,max_length=10, verbose_name=u"收件人")
    receiver = models.ForeignKey(EndUser, on_delete=models.CASCADE,  verbose_name=u"收件人", related_name="receiver_instance")
    create_time = models.DateTimeField(auto_now_add=True,verbose_name=u"下单时间")
    price = models.FloatField(null=True,blank=True,verbose_name=u"价格")
    def __unicode__(self):
        return self.id

class ExternalOrder(models.Model):
    external_id = models.CharField(max_length=10, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    external_order_id = models.CharField(max_length=1000, verbose_name=u"外部单号")
    external_checking_method = models.CharField(max_length=1000,verbose_name=u"查询方式")

class OrderStatus(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    id = models.CharField(max_length=10, verbose_name=u"订单号")
    time = models.DateTimeField(auto_now_add=True,verbose_name=u"时间")
    status = models.CharField(max_length=50,verbose_name=u"状态")
    location = models.CharField(max_length=50,verbose_name=u"当前位置")
    primKey= models.CharField(max_length=50, primary_key=True)
    def __unicode__(self):
        return self.order_id

class Quote(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    weight = models.FloatField(null=True,blank=True,verbose_name=u"重量")
    sender_address = models.CharField(null=True, max_length=50,verbose_name=u"发货地址")
    receiver_address = models.CharField(null=True, max_length=50,verbose_name=u"收货地址")
    create_time = models.DateTimeField(auto_now_add=True,verbose_name=u"下单时间")
    height = models.FloatField(null=True,blank=True,verbose_name=u"高度")
    width = models.FloatField(null=True,blank=True,verbose_name=u"宽度")
    length = models.FloatField(null=True,blank=True,verbose_name=u"长度")
    sender_info = models.ForeignKey(EndUser, on_delete=models.CASCADE, verbose_name=u"客户", related_name="sender_info")
    notes = models.CharField(null=True, max_length=500,verbose_name=u"备注")
    def __unicode__(self):
        return self.id

class QuoteAssignShippingUser(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    shipping_user_id = models.CharField(null=True, max_length=50, verbose_name=u"寄送人邮箱")
    primKey= models.CharField(max_length=100, primary_key=True)
    def __unicode__(self):
        return self.id

class QuoteBid(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    shipping_user_id = models.CharField(null=True, max_length=50, verbose_name=u"寄送人邮箱")
    bid_price = models.FloatField(null=True,blank=True,verbose_name=u"价格")
    primKey= models.CharField(max_length=100, primary_key=True)
    def __unicode__(self):
        return self.id

class ShippingUser(models.Model):
    user_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50,verbose_name=u"姓名")
    phone_number = models.CharField(max_length=50,verbose_name=u"联系方式")
    company_name = models.CharField(max_length=50,verbose_name=u"公司名")
    address = models.CharField(null=True, max_length=50,verbose_name=u"地址")
    postcode = models.CharField(max_length=50,verbose_name=u"邮政编码")
    def __unicode__(self):
        return self.user_id
