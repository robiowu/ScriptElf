# -*- coding: utf-8 -*-
"""
处理与窗体句柄相关的函数
"""
import win32gui
import win32api
import win32con
import pyautogui
import time
import random


def find_idxSubHandle(pHandle, winClass, winName, index=0):
    """
    已知子窗口的窗体类名和标题，寻找第index号个同类型的兄弟窗口
    :param pHandle: [int] 父窗体的句柄，没有父窗体就置0
    :param winClass: [str] 待查找的(子)窗口的类名，为 None 时则不限类名，不能与 winName 同时为None
    :param winName: [str] 待查找的(子)窗口的标题，为 None 时则不限标题名，不能与 winClass 同时为None
    :param index: [int] 待查找的(子)窗口的顺序值
    :return: 查找到的句柄值
    """
    assert (type(index) == int and index >= 0)
    assert (winClass is not None or winName is not None)
    assert index >= 0
    handle = 0
    for i in range(index+1):
        handle = win32gui.FindWindowEx(pHandle, handle, winClass, winName)
    return handle


def find_listSubHandle(pHandle, winClass, winName):
    """
    已知子窗口的窗体类名和标题，寻找满足条件的所有同类型的兄弟窗口
    :param pHandle: 父窗体的句柄，没有父窗体就置0
    :param winClass: 待查找的(子)窗口的类名
    :param winName: 待查找的(子)窗口的标题
    :return: <list> 查找到的满足条件的兄弟窗口的句柄的列表
    """
    assert (winClass is not None or winName is not None)
    result_list = []
    handle = 0
    handle = win32gui.FindWindowEx(pHandle, handle, winClass, winName)
    while(handle != 0):
        result_list.append(handle)
        handle = win32gui.FindWindowEx(pHandle, handle, winClass, winName)
    return result_list


def find_sub_handle(pHandle, winClassList):
    """
    用于查找指定的树状目录下的(子句柄)
    :param pHandle: input，父窗口句柄
    :param winClassList: List of dict。
    其中的每个dict都应该包含 winClass, winName, index, 即对应的是find_idxSubHandle()的后三个输入参数
    :return: 找到的句柄，int值
    """
    assert type(winClassList) == list
    for args in winClassList:
        pHandle = find_idxSubHandle(pHandle, args["winClass"], args["winName"], args["index"])
    return pHandle


def leftclick(handle, long_position, move: bool = False):
    """
    左键点击指定位置，点击完毕后自动弹起
    :param handle: 需要操作的句柄
    :param long_position: 操作的Lparam
    :param move: `bool` 是否需要将鼠标移过去
    :return:
    """
    if move:
        win32gui.SendMessage(handle, win32con.WM_MOUSEMOVE, 0, long_position)
    wparam = 1  # 鼠标左键对应的 wparam 消息参数值
    # 左键按下，延迟后放开
    win32gui.SendMessage(handle, win32con.WM_LBUTTONDOWN, wparam, long_position)
    time.sleep(0.2)
    win32gui.SendMessage(handle, win32con.WM_LBUTTONUP, wparam, long_position)


def leftclickXY(handle, x_position, y_position):
    """
    左键点击指定位置，点击完毕后自动弹起，使用XY坐标
    :param handle: 需要操作的句柄
    :param x_position: 点击的横坐标
    :param y_position: 点击的纵坐标
    :return:
    """
    x_position = int(x_position)
    y_position = int(y_position)
    long_position = win32api.MAKELONG(x_position, y_position)
    # 等效于下面这句话
    # long_position = (y_position << 4*4) + x_position  # 移位是按照bit移位的，所以16进制移一次位需要相当于bit移位4位
    # self.assert_equal(message="判断触击的坐标", actual=long_position, expect=(y_position << 4*4) + x_position)
    leftclick(handle=handle, long_position=long_position)
    return x_position, y_position


class Window:
    hwnd = 0
    first_hwnd = 0  # 这个是用来标识顶层父窗口的。只有顶层父窗口凯能用于置顶 setTop

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.first_hwnd = self.hwnd

    def show(self):
        """
        显示窗口
        :return:
        """
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def hide(self):
        """
        隐藏当前窗口
        :return:
        """
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    @property
    def ExStyle(self):
        """此控件的扩展样式
        """
        return win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)

    def setTop(self):
        """
        设置窗口置顶
        :return:
        """
        # win32con.SWP_NOMOVE | win32con.SWP_NOSIZE，前者是维持当前位置，后者是维持当前尺寸
        temp_style = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        win32gui.SetWindowPos(self.first_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, temp_style)

    def resetNotop(self):
        """
        设置窗口不置顶
        :return:
        """
        # win32con.SWP_NOMOVE | win32con.SWP_NOSIZE，前者是维持当前位置，后者是维持当前尺寸
        temp_style = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        win32gui.SetWindowPos(self.first_hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, temp_style)

    def randomClick(self, point_x, point_y, random_x=0, random_y=0, full_mock: bool = False):
        """
        随机点击，当random偏移量填入0时，则为直接点击
        :param point_x: [int] 客户端区域的期望点击的左上角点
        :param point_y: [int] 客户端区域的期望点击的左上角点
        :param random_x: [int] 随机的横坐标偏移量
        :param random_y: [int] 随机的纵坐标偏移量
        :param full_mock: `bool` 是否采用强制模拟（将鼠标移动过去，并使用pyAutoGui的鼠标点击）
        :return:
        """
        if point_x < 0 or point_y < 0:
            return
        random_x = int(random_x)
        random_y = int(random_y)
        result_x = point_x + random.randint(0, random_x)
        result_y = point_y + random.randint(0, random_y)
        if full_mock:
            self.setTop()
            left, top, _, _ = win32gui.GetWindowRect(self.hwnd)
            result_x += left
            result_y += top
            pyautogui.click(result_x, result_y, interval=0.2)
            # 不搞还原非置顶。因为制定相比于鼠标点击，是有延迟的。容易鼠标点了却还没置顶
            # self.resetNotop()
        else:
            result_x, result_y = leftclickXY(handle=self.hwnd, x_position=result_x, y_position=result_y)
        return result_x, result_y

    def highLight(self):
        """
        设置窗口边框绘制
        :return:
        """
        # win32con.SWP_NOMOVE | win32con.SWP_NOSIZE，前者是维持当前位置，后者是维持当前尺寸
        temp_style = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_DRAWFRAME
        # 设置之前先让它在顶部（非置顶）
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, 0, 0, 0, 0, temp_style)

    def noHighLight(self):
        """
        将之前的边框去掉
        :return:
        """
        # win32con.SWP_NOMOVE | win32con.SWP_NOSIZE，前者是维持当前位置，后者是维持当前尺寸
        temp_style = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        # 设置之前先让它在顶部（非置顶）
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, 0, 0, 0, 0, temp_style)

    def resize(self, width, height):
        """
        按照参数设置窗口大小尺寸
        :param width: [int] 要设置的宽度
        :param height: [int] 要设置的长度
        :return:
        """
        left, top, _, _ = win32gui.GetWindowRect(self.hwnd)
        win32gui.MoveWindow(self.hwnd, left, top, width, height, True)
        return

    def restore(self):
        """
        恢复窗口。具体效果不明
        :return:
        """
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)


if __name__ == '__main__':
    """
    测试逻辑
    """
    for i in range(0, 100):
        print(random.randint(0, 0))
