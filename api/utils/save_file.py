import os
import imghdr
import hashlib
import datetime
from PIL import Image

from attendance_system import settings


def save_img(image, child_folder):
    # 判断文件是否超出大小
    if image.size > 2097152:
        return 1

    # 临时存放
    image_temp_path = os.path.join(settings.MEDIA_ROOT, "temp", image.name)
    with open(image_temp_path, "wb") as f:
        for line in image:
            f.write(line)

    # 判断是否为图片
    imgType_list = {'jpg', 'bmp', 'png', 'jpeg', 'rgb', 'tif'}
    if imghdr.what(image_temp_path) not in imgType_list:
        return 2

    # 计算图片MD5后删除临时文件
    with open(image_temp_path, 'rb') as fp:
        image_data = fp.read()
    image_md5 = hashlib.md5(image_data).hexdigest()
    os.remove(image_temp_path)

    # 按时间创建路径存放图片
    # 年
    year_time = datetime.datetime.now().strftime('%Y')
    # 月
    month_time = datetime.datetime.now().strftime('%m')
    # 日
    day_time = datetime.datetime.now().strftime('%d')
    child_folder = child_folder.replace("/", "\\")
    image_folder_path = os.path.join(settings.MEDIA_ROOT, child_folder, year_time, month_time, day_time)

    if not os.path.isdir(image_folder_path):
        os.makedirs(image_folder_path)

    # 按文件MD5命名
    image_type = os.path.splitext(image.name)[1]
    image_path = os.path.join(image_folder_path, image_md5 + image_type)

    with open(image_path, "wb") as f:
        for line in image:
            f.write(line)

    child_folder = child_folder.replace("\\", "/")
    return child_folder + "/" + year_time + "/" + month_time + "/" + day_time + "/" + image_md5 + image_type