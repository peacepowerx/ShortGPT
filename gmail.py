import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_with_gmail(email, video_url):
    # 使用Gmail账号信息
    gmail_user = 'pixie.ai0@gmail.com'
    gmail_password = 'teqy ejlq zjnf uuvj'  # 这里建议使用应用程序密码

    # 创建邮件对象
    message = MIMEMultipart()
    message["From"] = gmail_user
    message["To"] = email
    message["Subject"] = "Your video is ready"
    
    # 邮件正文内容
    body_content = f"Your video is ready! You can view it at {video_url}"
    message.attach(MIMEText(body_content, "plain"))
    
    # 连接Gmail服务器
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)

    # 发送邮件
    server.sendmail(gmail_user, email, message.as_string())
    server.close()
    
    print("Email sent!")

# 视频处理完成后...
# send_email_with_gmail('ruoyu.zheng2016@gmail.com', 'video_url')

