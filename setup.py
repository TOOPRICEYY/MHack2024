from setuptools import setup, find_packages

setup(
    name='media_streaming_tool',
    version='0.2',
    packages=find_packages(),
    description='A tool to separate audio and video from a .webm file and extract frames as images.',
    author='Your Name',
    author_email='your.email@example.com',
    install_requires=[
        'Flask>=2.0.1',
        'requests>=2.25.1',
    ],
    extras_require={
        'dev': [
            'pytest>=6.2.5',
        ],
    },
    entry_points={
        'console_scripts': [
            'media_streaming_tool=media_streaming_tool.app:app.run',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)