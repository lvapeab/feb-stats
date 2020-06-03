# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='feb_stats',
      version='0.1',
      description='Parser for stats from the FEB website.',
      author='Alvaro Peris',
      author_email='lvapeab@gmail.com',
      url='https://github.com/lvapeab/feb-stats',
      download_url='https://github.com/lvapeab/feb-stats/archive/master.zip',
      license='MIT',
      classifiers=[
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          "License :: OSI Approved :: MIT License"
      ],
      install_requires=[
          "pandas",
          "lxml",
          "requests",
          "xlsxwriter",
          "pysimplegui",
      ],
      # entry_points={
      #     "console_scripts": [
      #         "foo = my_package.some_module:main_func",
      #         "bar = other_module:some_func",
      #     ],
      #     "gui_scripts": [
      #         "launch = launch:start_func",
      #     ]
      # },

      package_dir={'feb_stats': '.',
                   'feb_stats.feb_stats': 'feb_stats',
                   },
      packages=['feb_stats',
                'feb_stats.feb_stats',
                ],
      package_data={
          'feb_stats': ['data/*']
      }
      )
