# -*- coding: utf-8 -*-
"""
用来控制每个游戏脚本的基类
"""
import os
import cv2
from PIL import Image
import ScriptElf.mylog as mylog
import ScriptElf.findpic as findpic
import ScriptElf.system_cmd as system_cmd
from ScriptElf.winhandle import Window


class FeaturePic:
    def __init__(self, sizetuple, path, clicktuple, randomtuple, msg, **kwargs):
        """
        :param sizetuple: `tuple` 四个值。(l_multi, u_multi, r_multi, d_multi) 分别对应特征图在总图中的左上右下的倍率。
        :param path: `str` 对应图片的路径。路径中不能包含中文
        :param clicktuple: `tuple` 两个值。(x_multi, y_multi) 分别对应需要点击的点的波动范围在特征图的坐上右下倍率倍率。
        :param randomtuple:`tuple` 两个值。(randomx_multi, randomy_multi) 分别对应需要点击的店在特征图的坐上右下倍率倍率。
                            值得注意的是：这个值如果为None，则会自动填充特征值的大小。如果为(0, 0)，才是不做随机
        :param msg: `str` 特征名
        :param kwargs: 拓展参数。用于自定义逻辑
        """
        self.sizetuple = sizetuple
        self.path = path
        self.clicktuple = clicktuple
        self.randomtuple = randomtuple
        self.msg = msg
        if "threshold" in kwargs:
            self.threshold = kwargs["threshold"]
        if "save_feature" in kwargs:
            self.save_feature = kwargs["save_feature"]
        if "is_gray" in kwargs:
            self.is_gray = kwargs["is_gray"]
        else:
            self.is_gray = True
        pass

    @staticmethod
    def get_sizetuple(source_image: str, feature_image: str, _round: int = 3):
        """
        根据一个小图和一个大图，找出小图在大图中对应的比例
        :param source_image: `str`
        :param feature_image: `str`
        :param _round: `int`
        :return:
        """
        result = None
        source_image = findpic.get_cv2_numpy_image_from_file(source_image)
        feature_image = findpic.get_cv2_numpy_image_from_file(feature_image)

        height, width, channels = source_image.shape
        sub_height, sub_width, sub_channels = feature_image.shape

        left, up, _ = findpic.find_sub_pic(
            source_image=source_image, template=feature_image,
            left=0, top=0, right=width, bottom=height, is_gray=False)
        if left > 0:
            result = list()
            result.append(round(left / width, _round))
            result.append(round(up / height, _round))
            result.append(round((left + sub_width) / width, _round))
            result.append(round((up + sub_height) / height, _round))
        return result


class MyGameCase:
    """用来控制每个游戏脚本的对应游戏基类"""
    hwnd = 0
    window = None  # 窗体句柄。用来操作置顶、隐藏、拉伸等
    findpic_helper = None  # 找图helper类
    game_name = "MyGameCase"

    _log_helper = None
    _log_dir = None
    _log_name = None

    def __init__(self, hwnd, game_name, base_size: dict, dpi_multi=1, savelog=False):
        """
        :param hwnd: `int` 窗口句柄
        :param game_name: `str` 游戏名
        :param base_size: `dict` 用来标定我们脚本运行状态下，期望的客户区窗口大小。如 {"width": 540, "height": 960}
        后续将会用来对窗口截图缩放到对应的base_size之后在进行图像匹配
        :param dpi_multi: `float` DPI值
        """
        self.hwnd = hwnd
        self.dpi_multi = dpi_multi
        self.window = Window(self.hwnd)
        self.findpic_helper = findpic.FindPictureHelper(self.hwnd, dpi_multi=dpi_multi)
        self.game_name = game_name
        self.base_size = base_size

        # 确认文件目录合规，创建log
        assert (self.checkdir_char())
        self._log_dir = os.path.join(system_cmd.get_abs_appdata_path(), "ScriptElf", self.game_name)
        self._log_name = "%s[%d].log" % (game_name, hwnd)
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        self.__log_init(self._log_dir, self._log_name, savelog)

    def __log_init(self, log_abs_filepath, log_filename, savelog: bool):
        """
        初始化log模块
        :param log_abs_filepath: <str> log保存的目录的绝对路径
        :param log_filename: <str> log保存的文件名
        :return:
        """
        filename = os.path.join(log_abs_filepath, log_filename)
        self._log_helper = mylog.Logger(filename=filename, backcount=3, savelog=savelog)
        return

    def checkdir_char(self):
        """
        判断我们的文件名（游戏名）是否规范
        :return: <bool> 规范为True，不规范为False
        """
        if "" == self.game_name:
            return False
        forbid = "\\/:*?\"<>|"
        for char in forbid:
            if self.game_name.find(char) >= 0:
                return False
        return True

    def start_step(self, step_name):
        if not hasattr(self.start_step, "step_count"):
            self.start_step.step_count = 1
        self.log.info("执行步骤%d%s" % (self.start_step.step_count, step_name))

    @property
    def log(self):
        """
        Logger模块，之后直接调用对应的debug、info、warning、error等即可
        :return: <logger>
        """
        return self._log_helper.logger

    def save_log(self, info):
        return

    def find_feature(self, sub_image_path, subsize_tuple=None, save_feature=None, threshold=0.95, is_gray=True):
        """
        :param sub_image_path:
        :param subsize_tuple: 左上右下的倍率。原图为(0, 0, 1, 1)
        :param save_feature: `str` 如果为非None值，且特征图用的是全图挖块，那么会往该参数对应的图片路径保存挖块出来的特征图
        :param threshold: 相似值
        :param is_gray: `bool` 是否使用灰度图查找
        :return:
        """
        if not subsize_tuple:
            subsize_tuple = (0, 0, 1, 1)
        for i in subsize_tuple:
            # 过滤非法入参
            if i > 1 or i < 0:
                subsize_tuple = (0, 0, 1, 1)
                break
        self.findpic_helper.get_window_image()
        resized = cv2.resize(self.findpic_helper.numpy_image, (self.base_size["width"], self.base_size["height"]))
        subsize = (
            int(subsize_tuple[0] * self.base_size["width"]), int(subsize_tuple[1] * self.base_size["height"]),
            int(subsize_tuple[2] * self.base_size["width"]), int(subsize_tuple[3] * self.base_size["height"])
        )
        sub_image = findpic.get_cv2_numpy_image_from_file(sub_image_path)
        # numpy 的图片数据是 [y, x, c]
        if sub_image.shape[0] == self.base_size["height"] and sub_image.shape[1] == self.base_size["width"]:
            # 上到下, 左到右.
            sub_image = sub_image[subsize[1]:subsize[3], subsize[0]:subsize[2]]
            if save_feature:
                # sub_image_rgb = cv2.cvtColor(sub_image, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(sub_image)
                im.save(save_feature)
                im = Image.fromarray(resized[subsize[1]:subsize[3], subsize[0]:subsize[2]])
                im.save(f"{save_feature}.main.bmp")
        int_x, int_y, threshold_real = findpic.find_sub_pic(
            resized, *subsize,
            template=sub_image, threshold=threshold, is_gray=is_gray)
        if int_x >= 0:
            int_x += int(subsize_tuple[0] * self.base_size["width"])
        if int_y >= 0:
            int_y += int(subsize_tuple[1] * self.base_size["height"])
        return int_x, int_y, threshold_real

    def check_feature(self, feature: FeaturePic):
        threshold = feature.__dict__.get("threshold", 0.95)
        save_feature = feature.__dict__.get("save_feature")
        is_gray = feature.__dict__.get("is_gray", True)
        intx, inty, _ = self.find_feature(
            sub_image_path=feature.path, subsize_tuple=feature.sizetuple,
            save_feature=save_feature, threshold=threshold, is_gray=is_gray
        )
        if not feature.clicktuple:
            point_x = intx
            point_y = inty
        else:
            point_x = int(feature.clicktuple[0] * self.findpic_helper.width)
            point_y = int(feature.clicktuple[1] * self.findpic_helper.height)
        if not feature.randomtuple:
            random_x = int((feature.sizetuple[2] - feature.sizetuple[0]) * self.findpic_helper.width)
            random_y = int((feature.sizetuple[3] - feature.sizetuple[1]) * self.findpic_helper.height)
        else:
            random_x = int(feature.randomtuple[0] * self.findpic_helper.width)
            random_y = int(feature.randomtuple[1] * self.findpic_helper.height)
        result = {
            "intx": intx, "inty": inty, "threshold": _,
            "point_x": point_x, "point_y": point_y, "random_x": random_x, "random_y": random_y,
        }
        if intx >= 0 and inty >= 0:
            # self.log.info(f"找到 {feature.msg} 标志位")
            # self.log.info(f"标志图：{feature.path}")
            # self.log.info(f"坐标值: ( {intx}, {inty} )\t匹配值: {_}")
            # position_x, position_y = self.window.randomClick(
            #     point_x=point_x,
            #     point_y=point_y,
            #     random_x=random_x,
            #     random_y=random_y,
            #     full_mock=True
            # )
            # self.log.info(f"点击坐标: ( {position_x}, {position_y} )")
            result.update({"result": True})
            return result
        # self.log.info(f"没有找到 {feature.msg} 标志位")
        result.update({"result": False})
        return result
