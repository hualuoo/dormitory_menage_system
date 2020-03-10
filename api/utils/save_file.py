import os
import imghdr
import hashlib
import datetime
from PIL import Image

from attendance_system import settings


def save_img(image, child_folder):
    # 判断文件是否为空
    if image is None:
        return 0

    # 判断文件是否超出大小
    if image.size > 2097152:
        return 1

    # 临时存放
    image_temp_path = settings.MEDIA_ROOT.replace("\\", "/") + "/temp/" + image.name.replace("\"", "")
    with open(image_temp_path, "wb") as f:
        for line in image:
            f.write(line)

    # 判断是否为图片
    imgType_list = {'jpg', 'bmp', 'png', 'jpeg', 'rgb', 'tif'}
    image_type = imghdr.what(image_temp_path)
    if image_type not in imgType_list:
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
    image_folder_path = settings.MEDIA_ROOT.replace("\\", "/") + "/" + child_folder.replace("\\", "/") + "/" + year_time + "/" + month_time + "/" + day_time

    if not os.path.isdir(image_folder_path):
        os.makedirs(image_folder_path)

    # 按文件MD5命名
    image_path = image_folder_path + "/" + image_md5 + "." + image_type

    with open(image_path, "wb") as f:
        for line in image:
            f.write(line)

    return child_folder.replace("\\", "/") + "/" + year_time + "/" + month_time + "/" + day_time + "/" + image_md5 + "." + image_type