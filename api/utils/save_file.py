import os
import imghdr
import hashlib
import datetime
from PIL import Image
import random
import shutil

from attendance_system import settings


def save_img(image, child_folder):
    # 判断文件是否为空
    if image is None:
        return 0

    # 判断文件是否超出大小
    if image.size > 2097152:
        return 1

    # 临时存放(随机文件名)
    image_temp_path = settings.MEDIA_ROOT.replace("\\", "/") + "/temp/" + str(random.randint(0, 99999))
    with open(image_temp_path, "wb") as f:
        for line in image:
            f.write(line)

    # 判断是否为图片
    imgType_list = {'jpg', 'bmp', 'png', 'jpeg', 'rgb', 'tif'}
    image_type = imghdr.what(image_temp_path)
    if image_type not in imgType_list:
        return 2

    # 读取裁剪后的图片
    with open(image_temp_path, 'rb') as fp:
        image_data = fp.read()
    # 计算裁剪后的md5
    image_md5 = hashlib.md5(image_data).hexdigest()

    # 按时间创建路径存放图片
    # 年
    year_time = datetime.datetime.now().strftime('%Y')
    # 月
    month_time = datetime.datetime.now().strftime('%m')
    # 日
    day_time = datetime.datetime.now().strftime('%d')
    image_folder_path = settings.MEDIA_ROOT.replace("\\", "/") + "/" + child_folder.replace("\\",
                                                                                            "/") + "/" + year_time + "/" + month_time + "/" + day_time
    # 如果文件夹不存在则创建
    if not os.path.isdir(image_folder_path):
        os.makedirs(image_folder_path)
    # 按文件MD5命名
    image_path = image_folder_path + "/" + image_md5 + "." + image_type

    # 移动图片并重命名
    shutil.move(image_temp_path, image_path)

    return child_folder.replace("\\", "/") + "/" + year_time + "/" + month_time + "/" + day_time + "/" + image_md5 + "." + image_type


def save_img_and_crop_1_1(image, child_folder):
    # 判断文件是否为空
    if image is None:
        return 0

    # 判断文件是否超出大小
    if image.size > 2097152:
        return 1

    # 临时存放(随机文件名)
    image_temp_path = settings.MEDIA_ROOT.replace("\\", "/") + "/temp/" + str(random.randint(0,99999))
    with open(image_temp_path, "wb") as f:
        for line in image:
            f.write(line)

    # 判断是否为图片
    imgType_list = {'jpg', 'bmp', 'png', 'jpeg', 'rgb', 'tif'}
    image_type = imghdr.what(image_temp_path)
    if image_type not in imgType_list:
        return 2

    # 把图片裁剪成正方形
    pil_img = Image.open(image_temp_path)
    # 如果宽大于高
    if pil_img.size[0] > pil_img.size[1]:
        crop_img = pil_img.crop(
            (
                (pil_img.size[0] - pil_img.size[1]) /2,
                0,
                pil_img.size[0] - ((pil_img.size[0] - pil_img.size[1]) /2),
                pil_img.size[1]
            )
        )
    # 如果宽小于高
    if pil_img.size[0] < pil_img.size[1]:
        crop_img = pil_img.crop(
            (
                0,
                (pil_img.size[1] - pil_img.size[0]) /2,
                pil_img.size[0],
                pil_img.size[1] - ((pil_img.size[1] - pil_img.size[0]) / 2)
            )
        )
    # 宽高相等无需处理
    if pil_img.size[0] == pil_img.size[1]:
        crop_img = pil_img.crop(
            (
                0,
                0,
                pil_img.size[0],
                pil_img.size[1]
            )
        )
    # 保存裁剪后的文件
    crop_img.save(image_temp_path + '.' + image_type)
    # 删除未裁剪的图片
    os.remove(image_temp_path)

    # 读取裁剪后的图片
    with open(image_temp_path + '.' + image_type, 'rb') as fp:
        image_data = fp.read()
    # 计算裁剪后的md5
    image_md5 = hashlib.md5(image_data).hexdigest()

    # 按时间创建路径存放图片
    # 年
    year_time = datetime.datetime.now().strftime('%Y')
    # 月
    month_time = datetime.datetime.now().strftime('%m')
    # 日
    day_time = datetime.datetime.now().strftime('%d')
    image_folder_path = settings.MEDIA_ROOT.replace("\\", "/") + "/" + child_folder.replace("\\", "/") + "/" + year_time + "/" + month_time + "/" + day_time
    # 如果文件夹不存在则创建
    if not os.path.isdir(image_folder_path):
        os.makedirs(image_folder_path)
    # 按文件MD5命名
    image_path = image_folder_path + "/" + image_md5 + "." + image_type

    # 移动裁剪后的图片并重命名
    shutil.move(image_temp_path + '.' + image_type, image_path)

    return child_folder.replace("\\", "/") + "/" + year_time + "/" + month_time + "/" + day_time + "/" + image_md5 + "." + image_type