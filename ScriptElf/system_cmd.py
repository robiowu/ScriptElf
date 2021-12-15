# -*- coding: utf-8 -*-
"""
"""
import shutil
import os
import subprocess


def copy(source_path, dst_path):
    shutil.copyfile(source_path, dst_path)
    return


def move(source_path, dst_path):
    shutil.move(source_path, dst_path)
    return


def cmd_block(cmd_str):
    os.popen(cmd_str).read()
    return


def cmd_asyn(cmd_str):
    subprocess.Popen(cmd_str, shell=True)
    return


def remove_file(file_path):
    file_path = os.path.abspath(file_path)
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        print("——删除的文件不存在%s" % file_path)
    return


def remove_folder(folder_path):
    if os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
    else:
        print("——删除文件夹请输入正确的文件夹目录（绝对路径）")
    return


def get_abs_appdata_path():
    """
    获取当前用户的appdata路径，注意是appdata/roaming，返回的是绝对路径
    :return: 当前用户的appdata/roaming的绝对路径
    """
    return os.getenv("APPDATA")


if __name__ == '__main__':
    print(get_abs_appdata_path())
