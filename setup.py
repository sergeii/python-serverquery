from setuptools import setup

setup(
    name='python-serverquery',
    description='Game server status query package',
    version='0.5.0',
    author='Sergei Khoroshilov',
    author_email='kh.sergei@gmail.com',
    license='The MIT License',
    packages=['serverquery'],
    install_requires=['six'],
    tests_require=['six'],
    include_package_data=True,
)