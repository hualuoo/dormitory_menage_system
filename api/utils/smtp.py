import datetime

from django.core.mail import send_mail


def login_smtp(user):
    subject = '主题'  # 主题
    message = '内容'  # 内容
    sender = '考勤系统<i@hualuoo.com>'
    receiver = [user[0].email]  # 目标邮箱
    now_time = datetime.datetime.now()
    now_time_str = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
    html_message = '您的账户' + user[0].username + '在' + now_time_str + '登陆成功'   # 发送html格式
    send_mail(subject, message, sender, receiver, html_message=html_message)


def code_smtp(email, code):
    subject = '主题'  # 主题
    message = '内容'  # 内容
    sender = '考勤系统<i@hualuoo.com>'
    receiver = [email]  # 目标邮箱
    now_time = datetime.datetime.now()
    now_time_str = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
    html_message = '您的验证码为：' + code + '，该验证码有效期为5分钟。'   # 发送html格式
    return send_mail(subject, message, sender, receiver, html_message=html_message)