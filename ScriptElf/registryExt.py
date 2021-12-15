# coding: gbk
"""
ע�����ز���

ps:��֮ǰ���Զ����ű���ֱ���õ�֮������python3���䣬����δ֪
"""
import os
import winreg as _winreg


def OpenFullPathReg(regPath, sam=_winreg.KEY_READ):
    """
    @ Desc������ע���ȫ·����ע������ؾ����
    @ Author:
    @ INPUT: [str] regPath: ȫ·��ע���������磺HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr�����
    @ INPUT: [int] sam: ����Ȩ�ޣ����磺_winreg.KEY_ALL_ACCESS
    @ OUTPUT���ɹ�����ע�����, ʧ�ܷ���None
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
    @ Desc�����һ��ע������������м�ֵ��
    @ Author:
    @ INPUT: [str] regPath: ȫ·��ע���������磺HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr�����
    @ OUTPUT������ע����ֵ��ɵ��б�ÿһ����(name, value, type)
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
    @ Desc�����һ��ע��������������Ӽ���
    @ Author:
    @ INPUT: [str] regPath: ȫ·��ע���������磺HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr�����
    @ OUTPUT������ע����Ӽ���ɵ��б�
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
    @ Desc���ж�ע�����Ƿ���ڡ�
    @ Author:
    @ INPUT: [str] regPath: ȫ·��ע���������磺HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr�����
    @ OUTPUT�����ڷ���True�����򷵻�False��
    """

    key = OpenFullPathReg(regPath)
    if key is None:
        return False
    else:
        _winreg.CloseKey(key)
        return True


def IsValueExist(regPath, valueName):
    """
    @ Desc���ж�ע������ĳ��ֵ�Ƿ���ڡ�
    @ Author:
    @ INPUT: [str] regPath: ȫ·��ע���������磺HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr�����
    @ INPUT: [str] valueName: ע����ֵ���ơ�
    @ OUTPUT�����ڷ���True�����򷵻�False��
    """
    values = GetValues(regPath)
    for value in values:
        if value[0] == valueName:
            return True
    return False


def GetRegValue(regPath, valueName):
    """
    @ Desc����ȡע������ָ��Value��ֵ��
    @ Author:
    @ INPUT: [str] regPath: ȫ·��ע���������磺HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr�����
    @ INPUT: [str] valueName: ע����ֵ���ơ�
    @ OUTPUT������valueName��Ӧ��ֵ�������ڻ��쳣ʱ����None
    i.e. GetRegValue("HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr","Version"),���ذ汾����"10.x.xxxxx.201"
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
    @desc: ��Ĭ����ע����ļ�
    @ Author:
    @ INPUT: [str] regfilePath: �������ע����ļ���·��(����)
    @OUTPUT�����ص�����,�ɹ�����TRUE�����򷵻�FALSE
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
    desc: ����ĳ��ע����ֵ
    @ Author:
    @ INPUT: [str] regPath: ȫ·��ע���������磺HKEY_LOCAL_MACHINE\SOFTWARE\Tencent\QQPCMgr�����
    @ INPUT: [str] value_name: Ҫ���õ��Ӽ�ֵ������Ӧע�����ĳ��Ҫ���õ�ֵ��name
    @ INPUT: [str] value: Ҫ���õ�ֵ��
    @OUTPUT����������ע���ֵ���,�ɹ�����TRUE�����򷵻�FALSE
    """
    hkey = OpenFullPathReg(regPath, sam=_winreg.KEY_ALL_ACCESS)
    if hkey is None:
        return None
    try:
        _winreg.SetValueEx(hkey, value_name, 0, _winreg.REG_DWORD, value)
        # ret = _winreg.SetValueEx(hkey, value_name, 0, _winreg.REG_DWORD, value)
        # print(ret)    # ��Ϊ�����ɹ��Ļ� return �Ķ��� None������û������ȥ print ��
    except Exception as e:
        print(e, regPath, value_name)
        return None


if __name__ == '__main__':
    pass
