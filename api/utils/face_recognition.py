import os
import cv2
import numpy
import dlib

# 创建 Dlib 的正向人脸检测器
detector = dlib.get_frontal_face_detector()

# 创建 Dlib 的人脸5特征点检测器
predictor = dlib.shape_predictor("api/utils/data_dlib/shape_predictor_5_face_landmarks.dat")

# 导入 Dlib 预先学习的人脸识别模型
face_rec = dlib.face_recognition_model_v1("api/utils/data_dlib/dlib_face_recognition_resnet_model_v1.dat")


# 根据 参数(图片路径) 返回单张人脸图像的128D特征
def return_face_128d_features(image_path):
    '''
        参数：
            image_path(图片路径)，示例：
                "training_data/qiezi/timg-1.jpg"
        返回：
            face_128d_features(人脸128D特征)，示例：
                "-0.0839738 0.0859853   ... 0.0688491   0.0536951"
    '''

    # 采用 opencv 的 imread 方法根据图片路径参数读取图片
    img_read = cv2.imdecode(numpy.fromfile(image_path, dtype=numpy.uint8), -1)
    # 因 opencv 读取图片默认为 bgr 顺序，这里采用 opencv 的 cvtColor 把图片改为rgb顺序图
    img_gray = cv2.cvtColor(img_read, cv2.COLOR_BGR2RGB)
    # 采用 Dlib 的正向人脸检测器 预先检测人脸情况并存入 faces 数组
    faces = detector(img_gray, 1)

    # 判断检测的图片中是否不存在人脸或出现多张人脸，faces的长度即为检测到人脸的个数
    if len(faces) == 0:
        # 检测不到人脸
        os.remove(image_path)
        return 0
    if len(faces) > 1:
        # 检测人脸数大于2
        os.remove(image_path)
        return 1
    if len(faces) == 1:
        # 如果人脸数为 1
        # 采用 Dlib 的人脸5特征点检测器
        shape = predictor(img_gray, faces[0])
        # 生成单张人脸图像的128D特征
        face_128d_features = face_rec.compute_face_descriptor(img_gray, shape)
        return face_128d_features
