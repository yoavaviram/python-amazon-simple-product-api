import amazon

from setuptools import setup, find_packages


try:
  long_description=open('READMxE.md', 'r').read()
except IOError:
  long_description=""


setup(name='python-amazon-simple-product-api',
      version=amazon.__version__,
      description="A simple Python wrapper for the Amazon.com Product Advertising API",
      long_description=long_description,
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: Apache Software License",
          ],
      keywords='amazon, product advertising, api',
      author='Yoav Aviram',
      author_email='yoav.aviram@gmail.com',
      url='https://github.com/yoavaviram/python-amazon-simple-product-api',
      license='Apache 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=["bottlenose", "lxml", "python-dateutil"],
)
