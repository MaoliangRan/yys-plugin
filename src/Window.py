# -*- coding: UTF-8 -*-
# 窗体模块
import ctypes
import inspect
import threading
import time
import tkinter as tk
from concurrent.futures import thread
import tkinter
from tkinter import *
from tkinter import scrolledtext, messagebox

from YuHunModule import YuHun
from TuPoModule import TuPo
from YeYuanHuoModule import YeYuanHuo
from YuLingModule import YuLing
from HuoDongModule import HuoDong
from YongShengZhiHaiModule import YongShengZhiHai
from ChouCeZhiModule import ChouCeZhi
MSG = []
tasks = []
NeedCloseGame = False
NeedCloseSystem = False



def ChouCeZhiEntry(LogUI, NeedCloseGame, NeedCloseSystem):
    # 抽厕纸
    fun = ChouCeZhi()
    t = threading.Thread(target=fun.Run, args=(LogUI, NeedCloseGame, NeedCloseSystem))
    t.start()
    tasks.append(fun)

def YongShengZhiHaiEntry(LogUI, NeedCloseGame, NeedCloseSystem):
    # 通用活动
    fun = YongShengZhiHai()
    t = threading.Thread(target=fun.Run, args=(LogUI, NeedCloseGame, NeedCloseSystem))
    t.start()
    tasks.append(fun)

def HuoDongEntry(LogUI, NeedCloseGame, NeedCloseSystem):
    # 通用活动
    fun = HuoDong()
    t = threading.Thread(target=fun.Run, args=(LogUI, NeedCloseGame, NeedCloseSystem))
    t.start()
    tasks.append(fun)

def YuLingEntry(LogUI, NeedCloseGame, NeedCloseSystem):
    # 御灵
    fun = YuLing()
    t = threading.Thread(target=fun.Run, args=(LogUI, NeedCloseGame, NeedCloseSystem))
    t.start()
    tasks.append(fun)

def YeYuanHuoEntry(LogUI, NeedCloseGame, NeedCloseSystem):
    # 业原火
    fun = YeYuanHuo()
    t = threading.Thread(target=fun.Run, args=(LogUI, NeedCloseGame, NeedCloseSystem))
    t.start()
    tasks.append(fun)

def PersonalTupoEntry(LogUI, NeedCloseGame, NeedCloseSystem):
    # 个人突破
    fun = TuPo()
    t = threading.Thread(target=fun.Run, args=(LogUI, NeedCloseGame, NeedCloseSystem))
    t.start()
    tasks.append(fun)

def YuhunEntry(LogUI, NeedCloseGame, NeedCloseSystem):
    # 御魂
    #messagebox.showinfo('提示', '请确保两个帐号都已经进入组队房间并且阵容锁定')
    fun = YuHun()
    t = threading.Thread(target=fun.Run, args=(LogUI, NeedCloseGame, NeedCloseSystem))
    t.start()
    tasks.append(fun)


def StopAll(LogUI):
    try:
        global tasks
        for i in tasks:
            i.Terminate()
        tasks = []
        if LogUI is not None:
            LogUI.insert(END,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + ' 脚本停止\n')
            LogUI.see(END)
    except Exception as e:
        if LogUI is not None:
            tasks = []
            LogUI.insert(END,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + ' 脚本停止异常,可能已经停止,请重启再试\n')
            LogUI.see(END)
            print(e)


def Closing(app):
    try:
        StopAll(None)
        app.destroy()
    except Exception:
        sys.exit(-1)


def ShortCut(event):

    # 按f4 停止脚本
    # print("event.char =", event.char)
    # print("event.keycode =", event.keycode)
    # F4停止
    global app
    if event.keycode == 115:
        StopAll(Window.LogUI)


def ChangeEndActionWithGame():
    """
    选择是否体力用完关闭游戏
    """
    global NeedCloseGame
    NeedCloseGame = not NeedCloseGame
    global tasks
    for i in tasks:
        i.NeedCloseGame = NeedCloseGame
    print('NeedCloseGame', str(NeedCloseGame))


def ChangeEndActionWithSystem():
    """
    选择是否体力用完是否关机
    """
    global NeedCloseSystem
    NeedCloseSystem = not NeedCloseSystem
    global tasks
    for i in tasks:
        i.NeedCloseSystem = NeedCloseSystem
    print('NeedCloseSystem', NeedCloseSystem)


class Window:
    def __init__(self):
        self.initWidgets()

    def initWidgets(self):
        self.app = tk.Tk()  # 根窗口的实例(root窗口)
        self.app.geometry('250x550')
        self.app.title("yys")
        self.app.resizable(0, 0)  # 阻止Python GUI的大小调整
        frame1 = Frame(self.app, padx=20)
        frame1.pack(side=LEFT, fill=BOTH)
        #t1 = tk.Label(frame1, text='护肝小助手', font=("华文行楷", 22), borderwidth=2).pack(side=TOP, fill=X, expand=YES)

        frame2 = Frame(self.app)
        # t1 = tk.Label(frame2, text='日志', borderwidth=2, font=('微软雅黑', 10), height=1).pack(side=TOP, fill=X, expand=YES)
        t3 = scrolledtext.ScrolledText(frame2, font=('微软雅黑', 10))
        t3.pack(side=TOP, fill=X, expand=YES)
        #frame2.pack(side=RIGHT, fill=BOTH, expand=YES)
        Label(frame1,text='先打开挑战/组队面板(先锁默认邀接)',font =('微软雅黑', 7), borderwidth=2).pack(side=TOP, fill=X, expand=YES)
        Label(frame1,text='祝大家多出双速满速大头，多掉蓝票!',font =('微软雅黑', 7), borderwidth=2).pack(side=TOP, fill=X, expand=YES)
        # Button(frame1, command=lambda: TanSuoEntry(t3, NeedCloseGame, NeedCloseSystem), text='探索受邀(单开)', width=20).pack(
        #     side=TOP, expand=YES)
        Button(frame1, command=lambda: ChouCeZhiEntry(t3, NeedCloseGame, NeedCloseSystem), text='抽厕纸', width=20).pack(
            side=TOP, expand=YES)
        Button(frame1, command=lambda: HuoDongEntry(t3, NeedCloseGame, NeedCloseSystem), text='通用活动副本(可多开)', width=20).pack(
            side=TOP, expand=YES)
        Button(frame1, command=lambda: YuLingEntry(t3, NeedCloseGame, NeedCloseSystem), text='御灵副本(可多开)', width=20).pack(
            side=TOP, expand=YES)
        Button(frame1, command=lambda: YeYuanHuoEntry(t3, NeedCloseGame, NeedCloseSystem), text='业原火副本(可多开)', width=20).pack(
            side=TOP, expand=YES)
        Button(frame1, command=lambda: PersonalTupoEntry(t3, NeedCloseGame, NeedCloseSystem), text='个人突破8退4(单开)', width=20).pack(
            side=TOP, expand=YES)
        Button(frame1, command=lambda: YongShengZhiHaiEntry(t3, NeedCloseGame, NeedCloseSystem), text='永生之海副本(可双开)', width=20).pack(
            side=TOP, expand=YES)
        Button(frame1, command=lambda: YuhunEntry(t3, NeedCloseGame, NeedCloseSystem), text='御魂/觉醒副本(可双开)', width=20).pack(
            side=TOP, expand=YES)
        Checkbutton(frame1, text='体力用完关闭游戏（无效）', command=ChangeEndActionWithGame).pack(side=TOP, anchor='w')
        Checkbutton(frame1, text='体力用完立即关机（无效）', command=ChangeEndActionWithSystem).pack(side=TOP, anchor='w')
        # Label(frame1,text=' ',font =('微软雅黑', 7), borderwidth=2).pack(side=TOP, fill=X, expand=YES)
        # Label(frame1,text=' ',font =('微软雅黑', 7), borderwidth=2).pack(side=TOP, fill=X, expand=YES)
        Button(frame1, command=lambda: StopAll(t3), text='停止运行', width=20).pack(side=TOP, expand=YES)

        self.app.protocol("WM_DELETE_WINDOW", lambda: Closing(self.app))
        Window.LogUI = t3
        self.app.bind("<Key>", ShortCut)
        self.app.mainloop()  # 窗口的主事件循环，必须的。


if __name__ == '__main__':
    app = Window()
