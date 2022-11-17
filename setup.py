# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 17:12:14
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : setup.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import setuptools

def read_version():
    """
    读取打包的版本信息
    """
    with open("./NextBSpiders/__init__.py", "r", encoding="utf8") as f:
        for data in f.readlines():
            if data.startswith("NEXTBSPIDER_VERSION"):
                version = data.split("=")[-1][1:-1]
                return version
    
    return "1.0.0"

def read_readme():
    """
    读取README信息
    """
    with open("./README.md", "r", encoding="utf8") as f:
        return f.read()

def do_setup(**kwargs):
    try:
        setuptools.setup(**kwargs)
    except (SystemExit, Exception) as e:
        exit(1)

version = read_version()
long_description = read_readme()

do_setup(
    name="NextBSpiders",
    version=version,
    author="ddvv",
    author_email="dadavivi512@gmail.com",
    description="基于scrapy的telegram爬虫",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a232319779/NextBSpiders",
    packages=setuptools.find_packages(exclude=["tests"]),
    entry_points={
        "console_scripts": [
            "nextb-telegram-run-spider = NextBSpiders.cli.telegram_run_spider:run",
            "nextb-telegram-create-table = NextBSpiders.cli.telegram_create_table:run",
            "nextb-telegram-clear-dialog = NextBSpiders.cli.telegram_clear_dialog:run",
            "nextb-telegram-get-dialog = NextBSpiders.cli.telegram_get_dialog:run",
            "nextb-telegram-get-message = NextBSpiders.cli.telegram_get_message:run",
            "nextb-generate-user-message-csv = NextBSpiders.cli.generate_user_message_csv:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6,<3.9",
    keywords=[],
    license="MIT",
    include_package_data=True,
    install_requires=[
        "pyOpenSSL==22.0.0",
        "Scrapy==2.6.1",
        "SQLAlchemy==1.4.31",
        "Telethon==1.24.0",
        "Twisted==22.4.0",
        "pysocks==1.7.1",
    ],
)
