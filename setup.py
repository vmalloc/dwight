import os
import itertools
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "dwight_chroot", "__version__.py")) as version_file:
    exec(version_file.read())
    
setup(name="dwight-chroot",
      classifiers = [
          "Programming Language :: Python :: 2.7",
          ],
      description="Utility for creating and managing Linux based isolated development environments, using chroot",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      install_requires=[
          "python-unshare",
      ],
      scripts=[],
      namespace_packages=[],
      entry_points = dict(
          console_scripts = [
              "dwight  = dwight_chroot.scripts.dwight:main_entry_point",
              ]
          ),
          
      )
