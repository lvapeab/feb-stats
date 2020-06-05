# -- coding: utf-8 --
from setuptools import setup

setup(
    name='feb_stats',

    version='0.1',
    description='Parser for stats from the FEB website.',
    author='Alvaro Peris',
    author_email='lvapeab@gmail.com',
    url='https://github.com/lvapeab/feb-stats',
    download_url='https://github.com/lvapeab/feb-stats/archive/master.zip',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Spanish',
        'Operating System :: Microsoft :: Windows',
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        "pandas",
        "lxml",
        "requests",
        "xlsxwriter",
    ],
    packages=['feb_stats'],
    py_modules=['feb_stats'],
    package_dir={'feb_stats.feb_stats': 'feb_stats'}
)