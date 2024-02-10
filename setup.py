from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='alchemynger',
  version='0.1.5.2',
  author='Resheba',
  author_email='c90de11@gmail.com',
  description='Simple SQLAlchemy Connection Manager',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/Resheba/Alchemynger',
  packages=find_packages(),
  install_requires=[
    'sqlalchemy'
    ],
  classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
  ],
  keywords='sqlalchemy',
  project_urls={
    'Documentation': 'https://github.com/Resheba/Alchemynger'
  },
  python_requires='>=3.8'
)