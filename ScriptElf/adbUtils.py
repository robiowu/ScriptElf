import io
import os
import subprocess
from PIL import Image



class AdbUtils:
    def __init__(self, dev_id, use_adb=True, app_name=None, activity_name=None):
        if use_adb:
            self.adb = "adb"

        self.device_id = dev_id
        self.__connect_device__()
        self.app_name = app_name
        self.activity_name = activity_name

    def print(self, string):
        if "logger" in self.__dict__:
            self.logger.info(string)
        else:
            print(string)

    def __connect_device__(self):
        if self.device_id.find(":") < 0:
            # 说明这个device_id是设备名称，而不是无限链接的ip和port
            command = f"{self.adb} devices"

        else:
            # 构建ADB连接命令
            command = (f"{self.adb} "
                       f"connect"
                       f" {self.device_id}")
        self.print(command)
        try:
            result = subprocess.run(
                command, shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout, result.stderr
        except subprocess.SubprocessError as e:
            return None, str(e)

    def __lunch__(self):
        # 构建ADB启动应用命令
        command = (f"{self.adb} -s {self.device_id} "
                   f"shell am start -n "
                   f"{self.app_name}/{self.activity_name}")
        self.print(command)
        try:
            result = self.subprocess_run_print(command)
            return result.stdout, result.stderr
        except subprocess.SubprocessError as e:
            return None, str(e)

    def __kill_app__(self):
        command = (f"{self.adb} -s {self.device_id} "
                   f"shell am force-stop {self.app_name}")
        self.print(command)
        try:
            # 执行ADB停止应用命令，并捕获标准输出和错误
            result = self.subprocess_run_print(command)
            if result.stderr:
                return False, result.stderr
            return True, "Process killed successfully."
        except subprocess.SubprocessError as e:
            return False, str(e)

    def get_physical_size(self):
        wm_size = f"{self.adb} -s {self.device_id} shell wm size"
        wm_size = subprocess.run(wm_size, capture_output=True, text=True, shell=True)
        wm_size = wm_size.stdout
        lines = wm_size.split("\n")
        for line in lines:
            if "Physical size:" in line:
                temp = line.replace("Physical size: ", "").strip()
                width, height =  temp.split("x")
                return int(width), int(height)
        return None

    def subprocess_run_print(self, command, std_out=True, std_err=True):
        self.print(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        std_out and result.stdout and self.print(result.stdout.rstrip())
        std_err and result.stderr and self.print(result.stderr.rstrip())
        return result

    def get_game_status(self):
        cmd = f"{self.adb} -s {self.device_id} shell \"ps | grep {self.app_name}\""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout or result.returncode == 0:
                self.print("游戏正在运行")
                return True
            else:
                self.print("游戏已关闭")
                return False
        except subprocess.SubprocessError as e:
            self.print(f"游戏状态异常：{str(e)}")
            return False

    def init_game(self):
        if not self.get_game_status():
            self.start()

    def get_image(self):
        # 使用ADB命令获取屏幕截图，并使用Pillow库将其读入Python的内存中
        screencap_cmd = f"{self.adb} -s {self.device_id} shell screencap -p"
        proc = subprocess.Popen(screencap_cmd, stdout=subprocess.PIPE, shell=True)
        image_bytes = proc.stdout.read()  # 读取图像数据为字节流

        # Android的screencap命令在Windows上输出的数据可能需要替换\r\n为\n
        if os.name == 'nt':
            image_bytes = image_bytes.replace(b'\r\n', b'\n')

        # 使用Pillow的Image.open读取图像
        image = Image.open(io.BytesIO(image_bytes))
        return image

    def save_image(self, filepath):
        # 使用Pillow的Image.open读取图像
        image = self.get_image()
        image.save(filepath)
        return image

    def click(self, x, y):
        cmd = (f"{self.adb} "
               f"-s {self.device_id} "
               f"shell input tap {int(x)} {int(y)}")
        self.subprocess_run_print(command=cmd)


if __name__ == "__main__":
    ip = "127.0.0.1"
    port = "16448"
    a = AdbUtils(f"{ip}:{port}")
    w, h = a.get_physical_size()
    print(f"{w} : {h}")
