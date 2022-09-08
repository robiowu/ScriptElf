# -*- coding: utf-8 -*-
"""
找图模块
注：找的子图可以直接用QQ截图工具，然后保存成24位bmp格式即可
"""
import cv2
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import numpy
import os


def get_cv2_numpy_image_from_file(filepath, cv2_imreadmodes=cv2.IMREAD_UNCHANGED):
    """
    将一个图片文件读入到内存中，numpy类型
    :param filepath: <str> 要读入的图片路径，可以是相对路径也可以是绝对路径
    :param cv2_imreadmodes: <cv::ImreadModes> 读入的模式，值可以从cv2.IMREAD_XXXXX里找
    :return: <numpy> 等效的numpy对象，或者None（发生错误）
    """
    result = None
    filepath = os.path.abspath(filepath)
    if os.path.isfile(filepath):
        result = cv2.imread(filepath, cv2_imreadmodes)
        # 由于opencv读取图像是默认GBR读取，所以存取时按照RGB存放则会变绿
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        # print(filepath)
    return result


def get_cv2_numpy_image_from_PyCBitmap(PyCBitmap_Object):
    """
    将PyCBitmap对象转换cv2能处理的numpy标准对象
    :param PyCBitmap_Object: <PyCBitmap> 传入的PyCBitmap的bitmap对象
    :return: <numpy> 等效的numpy对象，或者None（发生错误）
    """
    numpy_image = None
    try:
        bmpinfo = PyCBitmap_Object.GetInfo()
        bmp_array = numpy.asarray(PyCBitmap_Object.GetBitmapBits(), dtype=numpy.uint8)
        pil_image = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmp_array, 'raw', 'BGRX', 0, 1)
        numpy_image = numpy.array(pil_image)
    except Exception as e:
        print(e)
        pass
    return numpy_image


def find_sub_pic(source_image, left, top, right, bottom, template, threshold=0.9, is_gray=True):
    """
    详情可查看https://www.jianshu.com/p/c20adfa72733，这篇文章写得不错
    匹配模式的问题可以看https://blog.csdn.net/coroutines/article/details/78229105
    使用opencv2的模板匹配功能（大图找小图）
    :param source_image: <numpy> 做找这个动作的基础大图
    :param left: <int> 大图要截的左坐标
    :param top: <int> 大图要截的上坐标
    :param right: <int> 大图要截的右坐标
    :param bottom: <int> 大图要截的下坐标
    :param template: <numpy> 要匹配的小图，即找的模板图
    :param threshold: <float> 匹配相似度，一定要匹配到一定程度了我们才返回值，越接近1越匹配，越接近-1越不匹配
    :param is_gray: <bool> 是否使用灰度图。使用的话性能会提高，不使用的话可以识别特定颜色
    :return: x:int, y:int, max_val:float 返回的最匹配的位置的左上角坐标，如果没有满足足够匹配度的点，则返回 -1,-1。并且返回相似度
    """
    left = int(left)
    top = int(top)
    right = int(right)
    bottom = int(bottom)
    # 根据输入，获取要处理的大图。
    # 注意，此处是先高度后宽度。numpy存储图片的方式是[y,x,c]
    target = source_image[top:bottom, left:right]
    # 执行模板匹配，采用的匹配方式cv2.TM_CCOEFF_NORMED，归一化相关系数匹配。即做相关系数匹配后会自动归一化(-1,1)
    if is_gray:
        # 转换为灰度图
        target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    else:
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 不同匹配模式需要看的值不同，详情见上面的文章。此处归一化相关系数匹配，越接近1越匹配，越接近-1越不匹配
    # print(max_val)
    # 绘制矩形边框，将匹配区域标注出来
    # min_loc：矩形定点
    # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
    # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
    # theight, twidth = template_gray.shape[:2]
    # cv2.rectangle(target_gray, max_loc, (max_loc[0] + twidth, max_loc[1] + theight), (0, 0, 225), 2)
    # 显示结果,并将匹配值显示在标题栏上
    # cv2.imshow("MatchResult", target)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    x = -1
    y = -1

    # 因为numpy是 [y, x, c] 的，因此坐标是 [y ,x] ，和我们日常使用相反
    loc = numpy.where(result >= threshold)  # 匹配程度大于%80的坐标 [y,x]
    for point in zip(*loc[::-1]):  # *号表示可选参数
        # right_bottom = (point[0] + twidth, point[1] + theight)
        # cv2.rectangle(target, pt, right_bottom, (0, 0, 255), 2)
        # 只要有 > 指定值的点，说明就有找到图，那么就选相似性最高的点即可
        x = max_loc[0]
        y = max_loc[1]
        break
    return x, y, max_val


class FindPictureHelper:
    """
    目前没找到python的动态捕捉截屏的方式，这里需要手工实现一下
    自己控制截屏与内存的释放（效率堪忧，因为每次又要开辟内存以及释放内存）
    """
    handle = None
    width = 0
    height = 0
    # 设备上下文，Divice Context。句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
    hwnd_DC = None
    # 创建设备描述表
    mfc_DC = None
    # 创建内存设备描述表
    save_DC = None
    # 图片的位图对象
    save_bit_map = None
    # 图片的numpy形式。因为openCV只接受numpy的输入
    numpy_image = None
    dpi_multi = 1

    def __init__(self, winhandle, dpi_multi=1):
        # 屏幕缩放比例
        self.dpi_multi = dpi_multi
        self.handle = winhandle
        left, top, right, bottom = win32gui.GetClientRect(winhandle)
        left, top = win32gui.ClientToScreen(winhandle, (left, top))
        right, bottom = win32gui.ClientToScreen(winhandle, (right, bottom))
        self.client_rect = (left, top, right, bottom)
        if (left, top, right, bottom) != win32gui.GetWindowRect(winhandle):
            temp = win32gui.GetWindowRect(winhandle)
            self.left_border = left - temp[0]
            self.top_border = top - temp[1]
            self.right_border = temp[2] - right
            self.bottom_border = temp[3] - bottom
        else:
            self.left_border = 0
            self.top_border = 0
            self.right_border = 0
            self.bottom_border = 0
        screen_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.width = right - left
        self.height = bottom - top
        if not (0 <= left <= screen_x and 0 <= top <= screen_y and 0 <= right <= screen_x and 0 <= bottom <= screen_y):
            self.width = int(self.width / self.dpi_multi)
            self.height = int(self.height / self.dpi_multi)
        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        self.hwnd_DC = win32gui.GetWindowDC(winhandle)
        # 通过hwndDC获得mfcDC(注意主窗口用的是win32gui库，操作位图截图是用win32ui库)
        self.mfc_DC = win32ui.CreateDCFromHandle(self.hwnd_DC)
        # 创建兼容DC，实际在内存开辟空间（ 将位图BitBlt至屏幕缓冲区（内存），而不是将屏幕缓冲区替换成自己的位图。同时解决绘图闪烁等问题）
        self.save_DC = self.mfc_DC.CreateCompatibleDC()
        # 创建位图对象准备保存图片
        self.save_bit_map = win32ui.CreateBitmap()
        # 为bitmap开辟空间
        self.save_bit_map.CreateCompatibleBitmap(self.mfc_DC, self.width, self.height)
        # 将位图放置在兼容DC，即将位图数据放置在刚开辟的内存里
        self.save_DC.SelectObject(self.save_bit_map)

    def get_window_image(self):
        """
        将当前句柄上下文指向的图片置于内存空间中，即
            刷新self.save_bit_map的值
        测试过了，在内存空间中的操作只是将当前时刻的窗口屏幕缓冲区copy到我们开辟的空间。
        且开辟的空间指向的内存空间不变。因此下次调用该函数时只是单纯地拿到最新的屏幕缓存并且复写替换到我们开辟的空间中，此时不会发生内存泄漏
        :return:
        """
        self.save_DC.BitBlt((0, 0), (self.width, self.height), self.mfc_DC, (0, 0), win32con.SRCCOPY)
        self.numpy_image = get_cv2_numpy_image_from_PyCBitmap(PyCBitmap_Object=self.save_bit_map)
        return

    def save_image(self, filepath, format=None):
        """
        用 PIL 来帮我们保存，PIL 的保存可以自动识别后缀名，或者是指定format
        :param filepath: 可以带后缀，然后format不填，则自动识别类型。具体看 PIL 的 Image.save()
        :param format: 可以是 "PNG" , "BMP" , "JPG", "JPEG"等等
        :return:
        """
        self.get_window_image()
        bmpinfo = self.save_bit_map.GetInfo()
        bmp_array = numpy.asarray(self.save_bit_map.GetBitmapBits(), dtype=numpy.uint8)
        pil_image = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmp_array, 'raw', 'BGRX', 0, 1)
        pil_image.save(filepath, format=format)
        return

    def save_bmp(self, filepath="zzx.bmp"):
        """
        保存当前内存中的bmp位图
        :return:
        """
        file_name = filepath
        if os.path.splitext(file_name)[-1] != "bmp":
            file_name = os.path.splitext(file_name)[0] + ".bmp"
        self.save_bit_map.SaveBitmapFile(self.save_DC, file_name)
        return

    def release_resource(self):
        """
        释放句柄信息避免内存泄泄漏
        :return:
        """
        try:
            win32gui.DeleteObject(self.save_bit_map.GetHandle())
            self.save_DC.DeleteDC()
        except Exception as e:
            pass
        return

    def find_sub_pic(self, sub_image_path, threshold=0.9):
        """
        简化并封装到工具类里的find_sub_pic
        :param sub_image_path: <str> 要找的子图的路径，可接受绝对路径和相对路径
        :param threshold: <float> [-1,1]，相似度
        :return: x:int, y:int, threshold_real:float
            返回的最匹配的位置的左上角坐标，如果没有满足足够匹配度的点，则返回 -1,-1。并且返回对应的特征匹配值
        """
        sub_image = get_cv2_numpy_image_from_file(sub_image_path)
        int_x, int_y, threshold_real = find_sub_pic(self.numpy_image, 0, 0,
                                                    self.width, self.height, template=sub_image, threshold=threshold)
        return int_x, int_y, threshold_real


if __name__ == "__main__":
    a = numpy.arange(9.).reshape(3, 3)
    print(a)
    print(numpy.where(a > 9))
    '''
    查看是否会内存泄漏
    test_win = FindPictureHelper(winhandle=1378758)
    for i in range(0, 2):
        test_win.get_window_image()
        print("第 %d 次执行：" % i, test_win.save_bit_map)
        test_win.save_image()
    test_win.release_resource()
    '''
