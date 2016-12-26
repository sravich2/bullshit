from setuptools import setup

setup(
      name='bullshit',
      version='0.1',
      description='Card Game',
      url='http://github.com/sravich2/bullshit',
      author='Sachin',
      author_email='sachin08@outlook.com',
      license='MIT',
      packages=['bullshit'],
      install_requires=[
          'pygame',
          'pygbutton'
      ],
      zip_safe=False,
)