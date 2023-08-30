import os
import random
import sys
import time
from tkinter import scrolledtext, messagebox
import cv2
import numpy
import numpy as np
import pyautogui
from PIL import ImageGrab
from goto import with_goto


pyautogui.FAILSAFE = False

# 初始化SIFT探测器，老版本写法：SIFT = cv2.xfeatures2d.SIFT_create()
SIFT = cv2.SIFT_create()


def ComputeScreenShot(screenShot):
    kp2, des2 = SIFT.detectAndCompute(screenShot, None)
    return kp2, des2

def GetLocation(target, kp2, des2):
    MIN_MATCH_COUNT = 10
    img1 = target

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
    x, y = random.randint(-factor, factor), random.randint(-factor, factor)
    return (originPos[0] + x, originPos[1] + y)


def Click(targetPosition):
    if targetPosition is None:
        print('未检测到目标')
    else:
        pyautogui.moveTo(targetPosition, duration=random.randint(100, 300) / 1000)
        pyautogui.click()


def LoadImgs():
    obj = {}
    path = os.getcwd() + '/img/tupo'
    file_list = os.listdir(path)

    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '/' + file
        a = cv2.imread(file_path, 0)
        obj[name] = a
    return obj


def GetScreenShot():
    screen = ImageGrab.grab()
    return cv2.cvtColor(numpy.asarray(screen), cv2.COLOR_RGB2BGR)


# 计算9个结界的x和y位置以及进攻退出位置
def GetJieJieLocation(imgs,kp,des,):
    locdictx={}
    locdicty={}
    escx = 0
    escy = 0
    obj = imgs['rank']
    pos1 = GetLocation(obj, kp, des)
    obj = imgs['close']
    pos2 = GetLocation(obj, kp, des)
    obj = imgs['ticket']
    pos3 = GetLocation(obj, kp, des)
    if pos1 is None or pos2 is None or pos3 is None:
        messagebox.showinfo('提示', '个人突破界面出错，请打开突破界面后或者尝试调整游戏界面大小至合适后重试！')
        sys.exit(-1)
        return None
    else:
        # escx, escy为进攻是退出按钮的位置
        escx = pos1[0]
        escy = pos3[1]
        # 根据排名和退出突破界面按钮二者的位置计算九个结界的位置
        x1 = numpy.int32(pos1[0] + (pos2[0] - pos1[0]) / 4)
        x2 = numpy.int32(pos1[0] + (pos2[0] - pos1[0]) / 2)
        x3 = numpy.int32(pos2[0] - (pos2[0] - pos1[0]) / 6)
        y1 = numpy.int32(pos1[1] - (pos1[1] - pos2[1]) / 6)
        y2 = numpy.int32(pos2[1] + (pos1[1] - pos2[1]) / 2)
        y3 = numpy.int32(pos2[1] + (pos1[1] - pos2[1]) / 6)
        locdictx["1"] = x1;locdicty["1"] = y3;
        locdictx["2"] = x2;locdicty["2"] = y3;
        locdictx["3"] = x3;locdicty["3"] = y3;
        locdictx["4"] = x1;locdicty["4"] = y2;
        locdictx["5"] = x2;locdicty["5"] = y2;
        locdictx["6"] = x3;locdicty["6"] = y2;
        locdictx["7"] = x1;locdicty["7"] = y1;
        locdictx["8"] = x2;locdicty["8"] = y1;
        locdictx["9"] = x3;locdicty["9"] = y1;
        return (locdictx , locdicty, escx, escy)

# 寻找某个目标点的位置，并做一定范围的随机位置处理
def GetTargetCheatPosition(imgs, targetname, holdtimemin, holdtimemax,factor):
    # 截图
    screen = GetScreenShot()
    kp2, des2 = ComputeScreenShot(screen)

    obj = imgs[targetname]
    # 获取位置
    pos = GetLocation(obj, kp2, des2)
    if pos is not None:
        return CheatPos(pos, factor)
    else:
        return None


class TuPo():
    def __init__(self):
        self._flag = False
        self.NeedCloseGame = False
        self.NeedCloseSystem = False

    @with_goto
    def Run(self, LogUI, NeedCloseGame, NeedCloseSystem):
        imgs = LoadImgs()
        # 9个结界的x和y坐标（注意方向）
        locdictx={}
        locdicty={}
        screen = GetScreenShot()
        # 为了优化速度，把计算屏幕截图的特征提取出来，避免重复运算
        kp2, des2 = ComputeScreenShot(screen)
        # 根据计算出的特征计算九个结界位置和退出按钮位置(在进攻界面识别会出问题/捂脸，这里直接计算出位置即可)
        locdictx, locdicty, escx, escy = GetJieJieLocation(imgs, kp2, des2)
        label.begin
        while self._flag is not True:
            # 失败次数
            losetimes = 0
            # 当前在第几个结界(1~9)
            jiejienum = 1
            # 是否刚点击了结界进而准备点击进攻
            attackready = 0
            #防止多次识别胜利页面导致当前在第几个结界出现错误
            next = 0
            # label报错不要理，编译可以通过
            # 重新开始检查元素标签
            label.restart
            # 图像识别结果字典(存的位置信息，如果未识别到则为None)
            resultobj = {}
            # 截屏
            screen = GetScreenShot()
            # 为了优化速度，把计算屏幕截图的特征提取出来，避免重复运算
            kp2, des2 = ComputeScreenShot(screen)

            # obj = imgs['refresh']
            # if GetLocation(obj,kp2,des2) is not None:
            #     print(666)
            # '''
            print("......")
            time.sleep(random.randint(1000, 1200) / 1000)
            print("jiejienum:"+str(jiejienum)+", losetimes:"+str(losetimes)+", attackready:"+str(attackready)+", next:"+str(next))
            print("图像识别判定中")
            for i in ['victoryend','victory','failure','noticket','reject','auto', 'attack','refresh','confirm']:
                obj = imgs[i]
                pos = GetLocation(obj, kp2, des2)
                if pos is not None:
                    # 如果是奖励界面，点击奖励达摩，然后重新识别界面
                    if i == 'victoryend':
                        print("victoryend")
                        pos = CheatPos(pos, 30)
                        Click(pos)
                        # 如果结界已经突破完，刷新统计数据重新开始
                        if jiejienum == 10:
                            print("九个结界突破完毕，刷新数据重新开始")
                            goto.begin
                        # 如果结界未突破完，继续识别界面进行判断
                        else:
                            goto.restart
                    # 如果是胜利页面，点击胜利页面，然后继续识别界面进行判断
                    elif i == 'victory':
                        print("victory")
                        Click(CheatPos(pos,20))
                        if next == 0:
                            jiejienum = jiejienum + 1
                            print(jiejienum)
                            next = 1
                        else:
                            print(jiejienum)
                            jiejienum = jiejienum
                        goto.restart
                    # 如果是失败页面，点击失败页面，记录失败次数，然后继续识别界面进行判断
                    elif i == 'failure':
                        print("failure")
                        losetimes = losetimes + 1
                        print("失败次数："+str(losetimes))
                        Click(CheatPos(pos,20))
                        goto.restart
                    # 如果有协作，直接关闭，然后重新开始识别当前界面
                    elif i == 'reject':
                        print("reject")
                        pos = CheatPos(pos, 5)
                        Click(pos)
                        # 重新开始识别界面
                        goto.restart
                    # 如果突破券耗尽直接退出
                    elif i == 'noticket':
                        print("noticket")
                        sys.exit(-1)
                    else:
                        print(str(i)+"位置已存储")
                        resultobj[i] = pos

            if ('attack' in resultobj) is True:
                print("点击attack:第"+str(jiejienum)+"个结界")
                # 已经点击结界，需要点击进攻
                Click(resultobj['attack'])
                attackready = 0
                next = 0
                time.sleep(random.randint(3000, 4000) / 1000)
                goto.restart
            elif ('refresh' in resultobj) is True:
                print("判断结界页面")
                # 处在突破主面板，需要根据当前进整体攻情况点击进攻或者刷新
                # 如果失败次数过多认为有个结界始终打不过，直接刷新数据重新开始判断流程
                if losetimes > 4:
                    print("失败超过四次直接refresh")
                    Click(resultobj['refresh'])
                    goto.begin
                else:
                    if attackready == 0:
                        print("点击结界")
                        jiejiecheatpos = CheatPos((locdictx[str(jiejienum)], locdicty[str(jiejienum)]), 10)
                        Click(jiejiecheatpos)
                        attackready = 1
                        goto.restart
                    # 如果点击了结界却没有识别出进攻点则认为结界已经突破
                    else:
                        print("该结界已突破")
                        attackready = 0
                        print("当前结界已经突破，跳转到下一个结界")
                        jiejienum = jiejienum + 1
                        next = 0
                        goto.restart

            elif ('confirm' in resultobj) is True:
                print("点击退出")
                # 处于点击了退出的页面，待点击退出
                Click(resultobj['confirm'])
                goto.restart
            elif ('auto' in resultobj) is True:
                # 处于进攻界面，需要根据当前整体进攻情况进行退出或者等待突破结束
                print(jiejienum)
                if jiejienum == 9 and losetimes < 4:
                    print("confirm退出")
                    Click((escx,escy))
                goto.restart
            else:
                print("do nothing")
                goto.restart
            # '''





    def Terminate(self):
        self._flag = True
        sys.exit(-1)


if __name__ == '__main__':
    pass
