from setuptools import setup, find_packages


version = '1.1.1'


setup(name='python-amazon-simple-product-api',
      version=version,
      description="A simple Python wrapper for the Amazon.com Product Advertising API",
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
          ],
      keywords='amazon, product advertising, api',
      author='Yoav Aviram',
      author_email='support@cleverblocks.com',
      url='https://github.com/yoavaviram/python-amazon-simple-product-api',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=["bottlenose"],
)
