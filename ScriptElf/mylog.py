# -*- coding: utf-8 -*-
"""
用来自定义打印日志
"""
import logging
from logging import handlers


class Logger(object):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename,
                 level='info', when='D',
                 backcount=3, fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        """
        自定义日志模块的初始化
        :param filename: <str> 你要保存的文件名，可使用绝对路径会长相对路径
        :param level: <level_relations> 最低捕获的日志级别
        :param when: <str> 日志的时间分片，可以参考下面的注释
        :param backcount: <int> 最多保留的日志个数
        :param fmt: <str> 日志的输出格式
        """
        self.logger = logging.getLogger(filename)
        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 这是设置采集日志的最低级别，默认是info，意思是debug级不采集，info及以上的采集
        self.logger.setLevel(self.level_relations.get(level))
        # 往屏幕上输出
        sh = logging.StreamHandler()
        # 设置屏幕上显示的格式
        sh.setFormatter(format_str)
        # 往文件里写入#指定间隔时间自动生成文件的处理器
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backcount, encoding='utf-8')
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时
        # D 天
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        # 设置文件里写入的格式
        th.setFormatter(format_str)
        # 把对象加到logger里
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


if __name__ == '__main__':
    log = Logger('ScriptElf_test.log', level='debug', backcount=1)
    log.logger.debug('debug')
    log.logger.info('info')
    log.logger.warning('警告')
    log.logger.error('报错')
    log.logger.critical('严重')
    Logger('error.log', level='error').logger.error('error')
