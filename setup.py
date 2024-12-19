# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="ScriptElf",
    version="2.4",
    description="robio's game elf",
    license="GPL Licence",

    author="robiowu",
    packages=find_packages(),
    platforms="windows",
    install_requires=['pywin32', 'opencv-python', 'pillow', 'numpy'],
)

# if __name__ == "__main__":
#     print(find_packages())
