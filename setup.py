from setuptools import setup

setup(
    name='running',
    version='0.1.0',
    description='User-friendly running pace calculator',
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
