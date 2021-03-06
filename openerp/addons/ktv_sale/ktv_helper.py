# -*- coding: utf-8 -*-
from osv import fields
from datetime import date,datetime,time
import logging
_logger = logging.getLogger(__name__)
#时间段选择
def time_for_selection(self,cr,uid,context = None):
     ret = [("%02i:00" % i,"%02i时30分" % i) for i in range(24)] + [("%02i:30" % i,"%02i时00分" % (i+1)) for i in range(24)]
     ret.sort()
     ret.pop()
     ret.append(("23:59","23时59分"))
     return ret

#价格列表
def price_list_for_selection(self,cr,uid,context = None):
    ret =[("ting_price","大厅价"),("room_price","包厢价"),("member_price","会员价"),("vip_price","贵宾价"),("a_price","A类价"),("b_price","B类价")]
    return ret

#房态定义
def room_states_for_selection(self,cr,uid,context = None):
    ret =[("free","空闲"),("in_use","使用"),("scheduled","预定"),("locked","锁定"),("checkout","已结账"),("buyout","买断"),("buytime","买钟"),("malfunction","故障"),("clean","清洁"),("debug","调试"),("visit","带客")]
    return ret
#男女
def sexes_for_select(self,cr,uid,context = None):
    ret=[("F","女"),("M","男")]
    return ret
#证件类型
def id_types_for_select(self,cr,uid,context = None):
    ret=[(1,"身份证"),(2,"驾驶证"),(3,"其他证件")]
    return ret

#根据0 1 2 3 4 5 6 分别返回星期缩写 min =0 ~ sun= 6
def weekday_str(weekday_int):
    weekday_dict = {
            0 : 'mon',
            1 : 'tue',
            2 : 'wed',
            3 : 'thu',
            4 : 'fri',
            5 : 'sat',
            6 : 'sun'
            }
    return weekday_dict[weekday_int]

def current_user_tz(obj,cr,uid,context = None):
    """
    获取当前登录用户的时区设置
    :param cursor cr 数据库游标
    :params integer uid 当前登录用户id
    """
    the_user = obj.pool.get('res.users').read(cr,uid,uid,['id','context_tz','name'])
    return the_user['context_tz']

def user_context_now(obj,cr,uid):
    """
    获取当前登录用户的本地日期时间
    :return 本地化的当前日期
    """
    tz = current_user_tz(obj,cr,uid)
    context_now = fields.datetime.context_timestamp(cr,uid,datetime.now(),{"tz" : tz})
    return context_now

def minutes_delta(time_from,time_to):
    '''
    计算给定两个时间的相差分钟数
    :param time_from string 形式是'09:30'的字符串,指的是起始时间
    :param time_to string 形式是'09:30'的字符串,指的是结束时间时间
    :return integer 两个时间的相差分钟数
    '''
    array_time_from = [int(a) for a in time_from.split(':')]
    array_time_to = [int(a) for a in time_to.split(':')]
    t1 = time(array_time_from[0],array_time_from[1])
    t2 = time(array_time_to[0],array_time_to[1])
    return (t2.hour - t1.hour)*60 + (t2.minute - t1.minute)

def context_now_minutes_delta(obj,cr,uid,time_to):
    '''
    计算当前时间到给定时间的相差分钟数,该计算是以当期登录用户所在时区进行计算的
    :param object obj osv对象
    :param cursot cr 数据库游标
    :param integer uid 当前登录用户
    :param string time_to 当前时间
    :return integer 两个时间的相差分钟数
    '''
    context_now = user_context_now(obj,cr,uid)
    return minutes_delta(context_now.strftime("%H:%M"),time_to)

def context_strptime(osv_obj,cr,uid,str_time):
    '''
    将给定的时间字符串转变为当日的时间，以当前登录用户的时区为标准
    :param osv_obj osv数据库对象
    :param cr db cursor
    :param int uid 当前登录用户
    :param str_time 形式为'09:30'的时间字符串
    :return datetime 计算过后的日期对象
    '''
    context_now = user_context_now(osv_obj,cr,uid)
    time_array = [int(a) for a in str_time.split(":")]
    ret = context_now.replace(hour=time_array[0],minute=time_array[1])
    return ret

def str_to_today_time(time):
    '''
    将给定的字符串转换为当日的datetime
    :params time 形式如 09:30:00形式的时间字符串
    :return 日期为当日,时间为传入参数的datetime对象
    '''
    now = datetime.now()
    array_time = [int(a) for a in time.split(':')]
    ret = now.replace(hour=array_time[0],minute = array_time[1],second = array_time[2])
    return ret

def utc_time_between(str_time_from,str_time_to,str_cur_time):
    """
    判断给定的时间字符串是否在给定的时间区间内
    由于对时间统一采用UTC时间保存,可能存在time_to < time_from的情况
    :params string str_time_from 形式类似 09:10的时间字符串
    :params string str_time_to 形式类似 09:10的时间字符串
    :params str_cur_time 要比较的时间字符串
    :return True 在范围内 else False
    """
    if str_time_to > str_time_from:
        return str_cur_time >= str_time_from and str_cur_time <= str_time_to
    else:
        #如果存在time_from 大于 time_to的情况,则说明时间跨天
        return (str_cur_time >= str_time_from and str_cur_time < '23:59:59') or (str_cur_time >='00:00:00' and str_cur_time <= str_time_to)

def calculate_present_minutes(buy_minutes,promotion_buy_minutes = 0,promotion_present_minutes = 0):
    """
    根据给定的参数计算赠送时长
    买钟时间(分钟数) / 设定买钟时长(分钟数) * 赠送时长
    :params buy_minutes integer 买钟时间
    :params promotion_buy_minutes integer 买钟优惠设置中设定的买钟时长
    :params promotion_present_minutes integer 买钟优惠设置中设定的赠送时长
    :return integer 赠送时长
    """
    #如果未设置优惠信息,则不赠送,直接返回买钟时间
    if not promotion_buy_minutes:
        return buy_minutes

    present_minutes = buy_minutes / promotion_buy_minutes * promotion_present_minutes

    return present_minutes
