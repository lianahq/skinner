from setuptools import setup, find_packages

setup(
    name = 'skinner',
    version = '0.0.1',
    description = 'Automatic WebApp Security Tests via Burp',
    classifiers = [
          "Programming Language :: Python :: 3.6"
    ],
    packages = find_packages(),
    package_data = {
        '': ['*.ini', '*.md', '*.txt', '*.zip']
    },
    author = 'Abdo',
    author_email = 'abdollah.shajadi@viidakko.fi',
    url = 'https://github.com/LianaTech/skinner',
    install_requires = open('requirements.txt').readlines(),
    entry_points = { 'console_scripts': ['skinner=__main__:main']},
)
