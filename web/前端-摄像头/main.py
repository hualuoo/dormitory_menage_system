import cv2
import pymysql
import json
import dlib
import numpy  # 数据处理的库 Numpy
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests


print("GPU计算是否启用：", dlib.DLIB_USE_CUDA)
mysql_host = "s1.mc.fyi"
mysql_post = 11452
mysql_user = "root"
mysql_password = "Qq111111"
mysql_db = "attendance_system"
login_url = "http://s1.mc.fyi:11453/login/"
login_header = {'Content-Type': 'application/json'}
login_username = "201635020501"
login_password = "Qq111111"
upload_url = "http://s1.mc.fyi:11453/access_control/"
# 判断识别阈值，欧式距离小于0.4即可判断为相似，越小越相似
threshold = 0.4


# 创建 Dlib 的正向人脸检测器
detector = dlib.get_frontal_face_detector()
# 创建 Dlib 的人脸5特征点检测器
predictor = dlib.shape_predictor("data/shape_predictor_5_face_landmarks.dat")
# 导入 Dlib 预先学习的人脸识别模型
face_rec = dlib.face_recognition_model_v1("data/dlib_face_recognition_resnet_model_v1.dat")
# OpenCv 调用摄像头 use camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# 设置视频参数 set camera
cap.set(3, 480)


def return_euclidean_distance(feature_1, feature_2):
    """
    计算两个128D特征向量间的欧式距离并返回
    :param feature_1: 128D特征向量1
    :param feature_2: 128D特征向量2
    :return: 欧式距离
    """
    feature_1 = numpy.array(feature_1)
    feature_2 = numpy.array(feature_2)
    # 欧式距离计算方法：
    #   先计算两个特征的差，再对每个子数进行平方处理，将平方处理后子数相加，最后对相加值开平方根
    dist = numpy.sqrt(numpy.sum(numpy.square(feature_1 - feature_2)))
    # dist = numpy.sqrt(sum((numpy.array(feature_1)-numpy.array(feature_2))**2))
    return dist


def get_user_face_data(get_time, data):
    """
    从数据库获取人脸数据(缓存五分钟)
    :param get_time: 上一次获取数据的时间
    :param data: 上次获取数据的内容
    :return: 获取数据的时间,获取数据的内容
    """
    if get_time == "" or get_time < (datetime.now() - timedelta(minutes=5)):
        # 连接数据库
        conn = pymysql.connect(
            host=mysql_host,
            port=mysql_post,
            user=mysql_user,
            password=mysql_password,
            db=mysql_db,
            charset='utf8'
        )
        # 创建游标
        cur = conn.cursor()
        sql = 'SELECT user_id,username,first_name,last_name,features FROM users_userface INNER JOIN users_user ON users_userface.user_id = users_user.id;'
        # 执行语句
        cur.execute(sql)
        # 关闭连接池
        cur.close()
        conn.close()
        return datetime.now(), cur.fetchall()
    return get_time, data


def change_cv2_draw(image, strs, local, sizes, colour):
    # 用于解决 OpenCV 绘图时中文出现乱码 方法类
    '''
        思路：
            1、OpenCV图片格式转换成PIL的图片格式；
            2、使用PIL绘制文字；
            3、PIL图片格式转换成OpenCV的图片格式；
        参数：
            image：OpenCV图片格式的图片
            strs：需要绘制的文字的内容
            local：需要绘制的文字的位置
            sizes：需要绘制的文字的大小
            colur：需要绘制的文字的颜色
    '''
    # 把图片改为rgb顺序图
    cv2img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 把OpenCV图片格式转换成PIL的图片格式
    pilimg = Image.fromarray(cv2img)
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(pilimg)
    # 字体的样式
    font = ImageFont.truetype("data/font/msyh.ttc", sizes, encoding="utf-8")
    # 绘制文字
    draw.text(local, strs, colour, font=font)
    # 把PIL图片格式转换成OpenCV的图片格式
    image = cv2.cvtColor(numpy.array(pilimg), cv2.COLOR_RGB2BGR)
    return image


# 账户登录
login_post_result = requests.post(url=login_url, headers=login_header,
                                  data=json.dumps({
                                      'username': login_username,
                                      'password': login_password
                                  }))
if json.loads(login_post_result.text)['is_superuser'] is False:
    print('请登录管理员账户！')
    quit()
login_token = json.loads(login_post_result.text)['token']
print(login_token)


# 保存图片
def save_image(image):
    save_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
    cv2.imwrite('temp/' + save_name, image)
    return save_name


# 上传图片
def upload_image(save_name, user_id, euclidean_distance):
    with open('temp/' + save_name, mode="rb")as f:  # 打开文件
        file = {
            "file": (save_name, f.read())  # 引号的file是接口的字段，后面的是文件的名称、文件的内容
        }
    upload_post_result = requests.post(url=upload_url + '?user_id=' + str(user_id) + '&euclidean_distance=' + str(euclidean_distance),
                                       headers={
                                           'Authorization': 'JWT ' + login_token
                                       },
                                       files=file)
    print("[BACKEND]", json.loads(upload_post_result.text)['detail'])


# 初始化数组等
get_time = datetime.strptime("2020-01-01", "%Y-%m-%d")
calculate_time = datetime.strptime("2020-01-01", "%Y-%m-%d")
data = ""
face_descriptor_old = ""
two_sec_min_euclidean_distance_list = []
two_sec_min_user_info_list = []
two_sec_min_img_list = []
name = ""
color = (0, 0, 0)


# 摄像头循环
while cap.isOpened():
    flag, img_read = cap.read()
    kk = cv2.waitKey(1)

    img_gray = cv2.cvtColor(img_read, cv2.COLOR_RGB2GRAY)
    # 人脸数 faces
    faces = detector(img_gray, 0)
    # 待会要写的字体 / font to write
    font = cv2.FONT_HERSHEY_COMPLEX

    if len(faces) != 0:
        # 矩形框
        # show the rectangle box
        for k, d in enumerate(faces):
            # 判断是否超出边界
            if d.right() > 640 or d.bottom() > 480 or d.left() < 0 or d.top() < 0:
                name = "请保证人脸不要超出边界。"
                color = (255, 0, 0)
            # 判断是否多个人
            elif len(faces) != 1:
                    name = "请保证摄像头范围内只存在一人。"
                    color = (255, 0, 0)
            else:
                # 采用 Dlib 的人脸5特征点检测器
                shape = predictor(img_gray, d)
                # 生成单张人脸图像的128D特征
                face_descriptor = face_rec.compute_face_descriptor(img_read, shape)

                # 从数据库获取人脸数据(缓存五分钟)
                get_time, data = get_user_face_data(get_time, data)

                euclidean_distance_list = []
                for one_data in data:
                    euclidean_distance_list.append(return_euclidean_distance(json.loads(one_data[4]), face_descriptor))

                """
                if face_descriptor_old != "":
                    if return_euclidean_distance(face_descriptor_old, face_descriptor) > 0.4:
                        print("检测到摄像头前换人了。")
                        name = ""
                        two_sec_min_euclidean_distance_list = []
                        two_sec_min_user_info_list = []
                        two_sec_min_img_list = []
                face_descriptor_old = face_descriptor
                """

                if calculate_time < (datetime.now() - timedelta(seconds=2)):
                    if two_sec_min_euclidean_distance_list:
                        if min(two_sec_min_euclidean_distance_list) < threshold:
                            index = two_sec_min_euclidean_distance_list.index(min(two_sec_min_euclidean_distance_list))
                            print("[MESSAGE]识别成功，你可能是：", two_sec_min_user_info_list[index][2],
                                  two_sec_min_user_info_list[index][3], "，欧式距离：", min(two_sec_min_euclidean_distance_list), "。")
                            save_name = save_image(two_sec_min_img_list[index])
                            upload_image(save_name, two_sec_min_user_info_list[index][0], min(two_sec_min_euclidean_distance_list))
                            name = two_sec_min_user_info_list[index][2] + two_sec_min_user_info_list[index][3]
                            color = (0, 255, 0)
                        else:
                            print("[MESSAGE]识别失败，请完善自己账户人脸信息或联系管理员！")
                            name = "识别失败，请完善自己账户人脸信息或联系管理员！"
                            color = (255, 0, 0)
                    two_sec_min_euclidean_distance_list = []
                    two_sec_min_user_info_list = []
                    two_sec_min_img_list = []
                    calculate_time = datetime.now()
                else:
                    two_sec_min_euclidean_distance_list.append(min(euclidean_distance_list))
                    two_sec_min_user_info_list.append(data[euclidean_distance_list.index(min(euclidean_distance_list))])
                    two_sec_min_img_list.append(img_read)

            # 画边框
            cv2.rectangle(img_read,
                          tuple([d.left(), d.top()]),
                          tuple([d.right(), d.bottom()]),
                          (255, 255, 255), 2)
            # 文字位置
            pos_namelist = tuple([d.left() + 5, d.bottom() - 25])
            img_read = change_cv2_draw(img_read, name, pos_namelist, 13, color)

    cv2.imshow("Dormitory Access Control System(Camera)", img_read)
