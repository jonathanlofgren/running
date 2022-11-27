from setuptools import setup
import os, sys

# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("python -m build")
    os.system("twine upload dist/*")
    sys.exit()

# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish-test":
    os.system("python -m build")
    os.system("twine upload -r testpypi dist/*")
    sys.exit()

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='running',
    version='0.1.3',
    description='User-friendly running pace calculator',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/jonathanlofgren/running',
    author='Jonathan Löfgren',
    author_email='lofgren021@gmail.com',
    py_modules=['running'],
    install_requires=[
        'Click',
    ],
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License'
    ],
    entry_points='''
        [console_scripts]
        running=running:running
    ''',
    project_urls={
        'Source': 'https://github.com/jonathanlofgren/running'
    }
)
