from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name='dyn53',
      version='0.0.1',
      description="Update route 53 dns records based on current IP address.",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author="José Fardello",
      author_email='jmfardello@uoc.edu',
      url='https://github.com/mapbox/dyn53',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[ 'boto3', 'dnspython', 'requests', 'certifi', ],
      extras_require={
          'test': ['pytest'],
      },
      entry_points="""
      [console_scripts]
      dyn53=dyn53.dyn53:run
      """
      )
