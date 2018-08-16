from setuptools import setup

def l_desc():
    with open("README.md", "r") as fh:
        return fh.read()

setup(
    name='pywebcopy',
    version='2.0.0',
    description='Mirrors online webpages and complete websites.',
    long_description=l_desc(),
    long_description_content_type="text/markdown",
    classifiers=[
    	'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
      ],
    keywords='pywebcopy website copy mirror downloader offline',
    url='https://github.com/rajatomar788/pywebcopy/',
    author='Raja Tomar',
    author_email='rajatomar788@gmail.com',
    license='MIT',
    packages=['pywebcopy'],
    install_requires=[
          'requests', 'bs4', 'lxml', 'html5lib'
      ],
    zip_safe=False
)