import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='BirDuster',
     version='1.0',
     scripts=['BirDuster.py'] ,
     author="tisf",
     description="A Dir bruteforect script imitating DirBuster's functionality",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/ytisf/BirDuster",
     install_requires=[
          'user_agent','colorama'
      ],
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 2",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
