from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='clem',
    version='0.1.0',
    description='Simple and lightweight text variation and templating language written in pure Python.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Jake Ledoux',
    author_email='contactjakeledoux@gmail.com',
    url='https://github.com/jakeledoux/clem',
    license='GNU General Public License v2.0',
    packages=find_packages(exclude=('tests', 'docs'))
)
