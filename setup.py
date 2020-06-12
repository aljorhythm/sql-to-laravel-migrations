import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aljorhythm", # Replace with your own username
    version="0.0.1",
    author="Joel Lim",
    author_email="103879u@gmail.com",
    description="Reverse SQL database into Laravel migrations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aljorhythm/sql-to-laravel-migrations.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)