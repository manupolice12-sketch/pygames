from setuptools import setup, find_packages 

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pygames-simplified",
    version="2.0.0",
    description="PyGame Simplified — A beginner-friendly wrapper around Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={'pygames': '.', 'pygames.pygames_engine': 'pygames_engine'},
    packages=['pygames', 'pygames.pygames_engine',
          'pygames.pygames_engine.engines',
          'pygames.pygames_engine.engines.power1',
          'pygames.pygames_engine.engines.power2',
          'pygames.pygames_engine.utils'],
    install_requires=[
        "pygame-ce>=2.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
    ],
)
project_urls={
    "Source": "https://github.com/manupolice12-sketch/pygames",
    "Bug Tracker": "https://github.com/manupolice12-sketch/pygames/issues",
},