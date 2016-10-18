import smtplib
from email.mime.text import MIMEText


def send_mail(subject, con='', fromaddr='1875486458@qq.com', toaddrs='1875486458@qq.com', username='1875486458@qq.com',
              password='vzzvzhvpprvdccji'):
    server = smtplib.SMTP_SSL('smtp.qq.com')
    server.login(username, password)
    msg = MIMEText(con)
    msg["Subject"] = subject
    msg["From"] = fromaddr
    msg["To"] = toaddrs
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.close()


def read_file_as_string(path):
    data = ""
    with open(path, 'r') as f:
        data = f.read()
    return data

def log(msg):
    print(msg)