# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 10:43:38
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : setup.py
# @Software : Visual Studio Code
# @WeChat   : NextB


from setuptools import setup, find_packages

depends = []

setup(
    name="NextBSpiders",
    version="1.0.0",
    packages=find_packages(exclude=[]),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "nextb-telegram-run-spider = NextBSpiders.cli.telegram_run_spider:run",
            "nextb-telegram-create-table = NextBSpiders.cli.telegram_create_table:run",
            "nextb-telegram-clear-dialog = NextBSpiders.cli.telegram_clear_dialog:run",
        ],
    },
    install_requires=depends,
    dependency_links=[],
    include_package_data=True,
    license="ddvv",
    author="ddvv",
    author_email="dadavivi512@gmail.com",
    description="NextBSpiders",
)
