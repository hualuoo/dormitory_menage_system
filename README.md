# 基于人脸识别的门禁管理系统(dormitory_menage_system)
## 项目介绍
    基于人脸识别的门禁管理系统(Python+Django+RESTframework+JsonWebToken+Redis+Dlib)
    该项目为宿舍门禁系统管理，并额外加入宿舍管理、水电费管理、在线充值、报修管理、系统日志等多项功能，详细见下方截图等。
    Django为后端、H5/CSS/JS为前端、MySQL为后端数据库、Redis为缓存、Dlib为人脸识别程序库。
    该项目为个人学校毕业设计使用，未考虑生产环境，后续开发随心。
    第一次尝试Django开发，也想尝试RESTful风格，虽然写得不怎样，希望能给人点帮助。

## 食用方法
1、下载项目文件
```
git pull https://github.com/hualuoo/dormitory_menage_system.git
```
2、运行MySQL和Redis，并在setting.py文件中配置数据库链接信息。
```
MySQL数据库使用5.7.27开发，建议使用相同版本(应该mysqlclient有向上兼容
项目自带Windows系统调试用Redis-x64-3.2.100，默认监听127.0.0.1，6379端口，requirepass为Qq111111
```
3、修改setting.py文件，进行下一步配置。
```
SMTP(邮箱SMTP功能，用于账户登录提示、邮箱发送验证码等功能)
ALiCloud_AFS(阿里云AFS人机验证，用于前端登录滑动验证)
CodePay(码支付，用户水电费充值时的在线支付)
QQConnect(QQ互联，用于前端QQ登录绑定)
```
4、生成数据表(像运行正常的Django项目一样使用指令)
```
python manage.py makemigrations
python manage.py migrate
```
5、导入初始系统设置数据
```
数据文件位置：/数据库/system_setting_systemsetting.sql
```
6、启动项目(像运行正常的Django项目一样使用指令)
```
python manage.py runserver 127.0.0.1:8080
```
## 系统运行截图
### 前端-后台[PC端]
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-54-09.537Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-55-26.348Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-55-42.322Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-56-15.175Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-56-51.027Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-57-33.868Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-57-58.470Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-58-10.981Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T11-59-38.666Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T12-00-20.094Z.png)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/PC%E7%AB%AF/%E7%81%AB%E7%8B%90%E6%88%AA%E5%9B%BE_2020-04-29T12-00-43.993Z.png)

### 前端-前台[移动端]
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-01-638_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-12-405_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-21-847_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-29-191_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-34-866_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-42-950_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-46-274_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-51-237_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-30-54-956_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-31-01-869_io.dcloud.HBui.jpg)
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E7%A7%BB%E5%8A%A8%E7%AB%AF/Screenshot_2020-04-29-20-31-06-044_io.dcloud.HBui.jpg)

### 前端-摄像头端
![image](https://github.com/hualuoo/dormitory_menage_system/blob/master/%E6%88%AA%E5%9B%BE/%E6%91%84%E5%83%8F%E5%A4%B4%E7%AB%AF/QQ%E6%88%AA%E5%9B%BE20200429203323.jpg)
