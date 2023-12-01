# -*- coding: utf-8 -*-
import datetime
import logging
import os
import random
import time
from tkinter import END

import cv2
import numpy
import numpy as np
import pyautogui
from PIL import ImageGrab
from matplotlib import pyplot as plt

pyautogui.FAILSAFE = False

# 初始化SIFT探测器，老版本写法：SIFT = cv2.xfeatures2d.SIFT_create()
SIFT = cv2.SIFT_create()


def ComputeScreenShot(screenShot):
    """
    由于屏幕分辨率高，计算耗时，这里优化一下
    :return:
    """
    kp2, des2 = SIFT.detectAndCompute(screenShot, None)
    return kp2, des2


def GetLocation(target, kp2, des2):
    """
    获取目标图像在截图中的位置
    :param target: 检测目标
    :return: 返回坐标(x,y) 与opencv坐标系对应
    """
    MIN_MATCH_COUNT = 10
    img1 = target  # cv2.cvtColor(target,cv2.COLOR_BGR2GRAY)# 查询图片
    # img2 = screenShot
    # img2 = cv2.cvtColor(screenShot, cv2.COLOR_BGR2GRAY)  # 训练图片
    # img2 = cv2.resize(img2, dsize=None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
    # 用SIFT找到关键点和描述符

    kp1, des1 = SIFT.detectAndCompute(img1, None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = img1.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        if M is not None:
            dst = cv2.perspectiveTransform(pts, M)
            arr = np.int32(dst)  #
            midPosArr = arr[0] + (arr[2] - arr[0]) // 2
            midPos = (midPosArr[0][0], midPosArr[0][1])

            # test

            # screen = ImageGrab.grab()
            # img2 = cv2.cvtColor(numpy.asarray(screen), cv2.COLOR_RGB2BGR)
            # show=cv2.circle(img2,midPos,30,(255,255,255),thickness=5)
            # cv2.imshow('s',show)
            # cv2.waitKey()
            # cv2.destroyAllWindows()

            return midPos
        else:
            return None
    else:
        return None


def CheatPos(originPos, factor=5):
    """
    对原始点击坐标进行随机偏移，防止封号
    :param originPos:原始坐标
    :param factor:最大随机偏移
    :return:
    """
    x, y = random.randint(-factor, factor), random.randint(-factor, factor)
    newPos = (originPos[0] + x, originPos[1] + y)
    return newPos


def Click(targetPosition):
    """
    点击屏幕上的某个点
    :param targetPosition: 要点击的目标点
    """
    if targetPosition is None:
        print('未检测到目标')
    else:
        pyautogui.moveTo(targetPosition, duration=0.20)
        pyautogui.click()
        time.sleep(random.randint(100, 300) / 1000)

        # time.sleep(random.randint(100, 150) / 1000)


def LoadImgs():
    """
    加载所有需要检测的目标图像
    :return:
    """
    obj = {}
    path = os.getcwd() + '/img/yongshengzhihai'
    file_list = os.listdir(path)

    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '/' + file
        a = cv2.imread(file_path, 0)
        obj[name] = a

    return obj


def GetScreenShot():
    """
    获取屏幕截图
    :return:
    """
    screen = ImageGrab.grab()
    # screen.save('screen.jpg')
    # screen = cv2.imread('screen.jpg')
    screen = cv2.cvtColor(numpy.asarray(screen), cv2.COLOR_RGB2BGR)
    return screen


class YongShengZhiHai():
    def __init__(self):
        self._flag = False
        self.NeedCloseGame = False
        self.NeedCloseSystem = False
        self.PlayerNumber = 2

    def Run(self, LogUI, NeedCloseGame, NeedCloseSystem, PlayerNumber):
        imgs = LoadImgs()
        tips = {}
        self.PlayerNumber = PlayerNumber
        tips['end1'] = "胜利界面"
        tips['end2'] = "胜利达摩"
        tips['tiaozhan'] = "挑战按钮"
        tips['reject'] = "协作拒绝按钮"
        tips['invite'] = "组队邀请按钮"
        while self._flag is not True:
            screen = GetScreenShot()
            # WindowShape = screen.shape
            #result = []
            resultobj ={}
            # 为了优化速度，把计算屏幕截图的特征提取出来，避免重复运算
            kp2, des2 = ComputeScreenShot(screen)
            # 乱移动一下鼠标，防止有时候队长先进入组队页面后鼠标停留在挑战处导致无法识别
            # pyautogui.moveTo((random.randint(100, 1000),random.randint(100, 1000)), duration=0.15)
            for i in ['end1', 'end2', 'reject','tiaozhan','invite']:
                print("图像识别判定中，寻找:"+tips[i])
                obj = imgs[i]
                pos = GetLocation(obj, kp2, des2)
                if pos is not None:
                    if i == 'end1':
                        time.sleep(random.randint(80, 200) / 1000)
                        pos = CheatPos(pos, 10)
                        resultobj['end1']=pos
                    elif i == 'end2':
                        newPos = (pos[0] + 80, pos[1] + 80)
                        pos = CheatPos(newPos, 10)
                        resultobj['end2']=pos
                    elif i == 'invite':
                        pos = CheatPos(pos, 20)
                        resultobj['invite']=pos
                    elif i == 'tiaozhan':
                        resultobj['tiaozhan']=CheatPos(pos,15)
                    elif i == 'reject':
                        pos = CheatPos(pos, 3)
                        resultobj['reject']=pos
                else:
                     resultobj[i] = None
            # 检查结果
            print('yuhun player number:', self.PlayerNumber)
            if resultobj['reject'] is not None:
                print("关闭邀请")
                Click(resultobj['reject'])
                if resultobj['end1'] is not None:
                    print("点击胜利界面")
                    Click(resultobj['end1'])
                if resultobj['end2'] is not None:
                    print("点击胜利达摩")
                    Click(resultobj['end2'])
            elif resultobj['end1'] is not None:
                print("点击胜利界面")
                Click(resultobj['end1'])
                if resultobj['end2'] is not None:
                    print("点击胜利达摩")
                    Click(resultobj['end2'])
            elif resultobj['end2'] is not None:
                print("点击胜利达摩")
                Click(resultobj['end2'])
                if resultobj['end1'] is not None:
                    print("点击胜利界面")
                    Click(resultobj['end1'])
            elif self.PlayerNumber is 3 and resultobj['invite'] is not None:
                print("三人队有队友未加入，等待一会")
                time.sleep(0.5)
                if resultobj['end1'] is not None:
                    print("点击胜利界面")
                    Click(resultobj['end1'])
                if resultobj['end2'] is not None:
                    print("点击胜利达摩")
                    Click(resultobj['end2'])
            elif resultobj['tiaozhan'] is not None:
                print("点击挑战")
                Click(resultobj['tiaozhan'])
                time.sleep(40)
                # 乱移动一下鼠标，防止有时候队长先进入组队页面后鼠标停留在挑战处导致无法识别
                pyautogui.moveTo((random.randint(100, 1000),random.randint(100, 1000)), duration=0.15)
            # for i in resultobj:
            #     if i is not None:
            #         if i=='tiaozhan':
            #             if resultobj[i] is not None and 'end1' in resultobj and resultobj['end1'] is not None:
            #                 print("点击胜利界面")
            #                 Click(resultobj['end1'])
            #             elif resultobj[i] is not None and 'end2' in resultobj and resultobj['end2'] is not None:
            #                 print("点击胜利达摩")
            #                 Click(resultobj['end2'])
            #             if resultobj[i] is not None:
            #                 print("点击挑战按钮")
            #                 Click(resultobj[i])
            #                 print("进入挑战，等待一段时间再进行图像识别")
            #                 time.sleep(40)
            #         else:
            #             if resultobj[i] is not None:
            #                 print("点击"+tips[i])
            #                 Click(resultobj[i])
            # time.sleep(random.randint(1500, 1800) / 1000)


    def Terminate(self):
        self._flag = True


if __name__ == '__main__':
    pass
