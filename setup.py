from setuptools import setup, find_packages

# guide: https://packaging.python.org/en/latest/tutorials/packaging-projects/

# 定义发布的包文件的信息
setup(
    name="ngixqlrc",  # 发布的包文件名称
    version="20240606.1",  # 发布的包的版本序号
    description="Utilities for processing ``ngix qim`` (imitating sound) lyric files",  # 发布包的描述信息
    author="xep",  # 发布包的作者信息
    author_email="mxy0268@qq.com",  # 作者联系邮箱信息
    # py_modules = ['checi3',
    #               'connect2',
    #               'direction',
    #               'utility',
    #               '__init__',],  # 发布的包中的模块文件列表
    packages=find_packages(where='src'),  
    package_dir={'': 'src'},  
    python_requires=">=3.9",
    requires=[
        'lxml',
        'imgkit',
        'MarkdownSuperscript',
        'markdown',
    ]
)
