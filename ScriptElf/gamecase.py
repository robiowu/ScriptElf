# -*- coding: utf-8 -*-
"""
用来控制每个游戏脚本的基类
"""
import ScriptElf.mylog as mylog
import ScriptElf.findpic as findpic
import ScriptElf.system_cmd as system_cmd
from ScriptElf.winhandle import Window
import os


class MyGameCase:
    """用来控制每个游戏脚本的对应游戏基类"""
    hwnd = 0
    window = None   # 窗体句柄。用来操作置顶、隐藏、拉伸等
    findpic_helper = None  # 找图helper类
    game_name = "MyGameCase"

    _log_helper = None
    _log_dir = None
    _log_name = None

    def __init__(self, hwnd, game_name, dpi_multi=1):
        self.hwnd = hwnd
        self.dpi_multi = dpi_multi
        self.window = Window(self.hwnd)
        self.findpic_helper = findpic.FindPictureHelper(self.hwnd, dpi_multi=dpi_multi)
        self.game_name = game_name

        # 确认文件目录合规，创建log
        assert(self.checkdir_char())
        self._log_dir = os.path.join(system_cmd.get_abs_appdata_path(), "ScriptElf", self.game_name)
        self._log_name = "%s[%d].log" % (game_name, hwnd)
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        self.__log_init(self._log_dir, self._log_name)

    def __log_init(self, log_abs_filepath, log_filename):
        """
        初始化log模块
        :param log_abs_filepath: <str> log保存的目录的绝对路径
        :param log_filename: <str> log保存的文件名
        :return:
        """
        filename = os.path.join(log_abs_filepath, log_filename)
        self._log_helper = mylog.Logger(filename=filename, backcount=3)
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
