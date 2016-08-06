# -*- coding: utf-8 -*-
from codecs import open as codecs_open
from setuptools import setup, find_packages


with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name='dyn53',
      version='0.0.2',
      python_requires='>3.2',
      description="Update route 53 dns records based on current IP address.",
      long_description=long_description,
      keywords='',
      author="José Fardello",
      author_email='jmfardello@gmail.com',
      url='https://github.com/jfardello/dyn53',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite="tests.suite",
      install_requires=['boto3', 'dnspython', 'requests', 'certifi', ],
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      entry_points="""
      [console_scripts]
      dyn53=dyn53.dyn53:run
      """
      )
