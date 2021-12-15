# coding: gbk
"""
注册表相关操作

ps:从之前的自动化脚本中直接拿的之后做的python3适配，作者未知
"""
import os
import winreg as _winreg


def OpenFullPathReg(regPath, sam=_winreg.KEY_READ):
    """
    @ Desc：根据注册表全路径打开注册表，返回句柄。
    @ Author:
    @ INPUT: [str] regPath: 全路径注册表键，比如：HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr（必填）
    @ INPUT: [int] sam: 访问权限，比如：_winreg.KEY_ALL_ACCESS
    @ OUTPUT：成功返回注册表句柄, 失败返回None
    """
    rootKeys = ["HKEY_CLASSES_ROOT", "HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE", "HKEY_USERS", "HKEY_CURRENT_CONFIG"]
    pos = -1
    for rootKey in rootKeys:
        pos = regPath.find(rootKey)
        if pos != -1:
            break

    if pos != -1:
        if rootKey == "HKEY_CLASSES_ROOT":
            regRoot = _winreg.HKEY_CLASSES_ROOT
        elif rootKey == "HKEY_CURRENT_USER":
            regRoot = _winreg.HKEY_CURRENT_USER
        elif rootKey == "HKEY_LOCAL_MACHINE":
            regRoot = _winreg.HKEY_LOCAL_MACHINE
        elif rootKey == "HKEY_USERS":
            regRoot = _winreg.HKEY_USERS
        elif rootKey == "HKEY_CURRENT_CONFIG":
            regRoot = _winreg.HKEY_CURRENT_CONFIG
        else:
            print("Wrong reg path: ", regPath)
            return None
    else:
        print("Wrong reg path: ", regPath)
        return None

    subKey = regPath[pos + len(rootKey) + 1:]
    try:
        key = _winreg.OpenKey(regRoot, subKey, 0, sam)
    except:
        print("Fail to open: ", regPath)
        return None
    return key


def GetValues(regPath):
    """
    @ Desc：获得一个注册表键下面的所有键值。
    @ Author:
    @ INPUT: [str] regPath: 全路径注册表键，比如：HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr（必填）
    @ OUTPUT：所有注册表键值组成的列表，每一项是(name, value, type)
    """

    values = []
    key = OpenFullPathReg(regPath)
    if key is None:
        return values
    try:
        i = 0
        while True:
            name, value, type = _winreg.EnumValue(key, i)
            values.append((name, value, type))
            i = i + 1
    except WindowsError:
        return values


def GetSubKeys(regPath):
    """
    @ Desc：获得一个注册表键下面的所有子键。
    @ Author:
    @ INPUT: [str] regPath: 全路径注册表键，比如：HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr（必填）
    @ OUTPUT：所有注册表子键组成的列表。
    """

    subKeys = []
    key = OpenFullPathReg(regPath)
    if key is None:
        return subKeys
    try:
        i = 0
        while True:
            name = _winreg.EnumKey(key, i)
            subKeys.append(name)
            i = i + 1
    except WindowsError:
        return subKeys


def IsKeyExist(regPath):
    """
    @ Desc：判断注册表键是否存在。
    @ Author:
    @ INPUT: [str] regPath: 全路径注册表键，比如：HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr（必填）
    @ OUTPUT：存在返回True，否则返回False。
    """

    key = OpenFullPathReg(regPath)
    if key is None:
        return False
    else:
        _winreg.CloseKey(key)
        return True


def IsValueExist(regPath, valueName):
    """
    @ Desc：判断注册表键下某个值是否存在。
    @ Author:
    @ INPUT: [str] regPath: 全路径注册表键，比如：HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr（必填）
    @ INPUT: [str] valueName: 注册表键值名称。
    @ OUTPUT：存在返回True，否则返回False。
    """
    values = GetValues(regPath)
    for value in values:
        if value[0] == valueName:
            return True
    return False


def GetRegValue(regPath, valueName):
    """
    @ Desc：获取注册表键下指定Value的值。
    @ Author:
    @ INPUT: [str] regPath: 全路径注册表键，比如：HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr（必填）
    @ INPUT: [str] valueName: 注册表键值名称。
    @ OUTPUT：返回valueName对应的值，不存在或异常时返回None
    i.e. GetRegValue("HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr","Version"),返回版本号如"10.x.xxxxx.201"
    """

    value = None
    hkey = OpenFullPathReg(regPath)
    if hkey is None:
        return None
    try:
        value = _winreg.QueryValueEx(hkey, valueName)[0]
        return value
    except Exception as e:
        print(e, regPath, valueName)
        return None


def ImportRegistry(regfilePath):
    """
    @desc: 静默导入注册表文件
    @ Author:
    @ INPUT: [str] regfilePath: 待导入的注册表文件的路径(必填)
    @OUTPUT：返回导入结果,成功返回TRUE，否则返回FALSE
    """
    if os.path.isfile(regfilePath):
        cmd = "regedit /s %s >nul" % regfilePath
        if os.system(cmd) == 0:
            print("import registry file succeed")
            return True
        else:
            print("Fail to import registry file")
            return False
    else:
        print("%s is not a file" % regfilePath)
        return False


def SetValue(regPath, value_name, value):
    """
    desc: 设置某项注册表的值
    @ Author:
    @ INPUT: [str] regPath: 全路径注册表键，比如：HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr（必填）
    @ INPUT: [str] value_name: 要设置的子键值，即对应注册表中某项要设置的值的name
    @ INPUT: [str] value: 要设置的值。
    @OUTPUT：返回设置注册表值结果,成功返回TRUE，否则返回FALSE
    """
    hkey = OpenFullPathReg(regPath, sam=_winreg.KEY_ALL_ACCESS)
    if hkey is None:
        return None
    try:
        _winreg.SetValueEx(hkey, value_name, 0, _winreg.REG_DWORD, value)
        # ret = _winreg.SetValueEx(hkey, value_name, 0, _winreg.REG_DWORD, value)
        # print(ret)    # 因为操作成功的话 return 的都是 None，所以没有意义去 print 它
    except Exception as e:
        print(e, regPath, value_name)
        return None


if __name__ == '__main__':
    pass
