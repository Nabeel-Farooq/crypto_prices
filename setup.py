from pathlib import Path

import setuptools


BASE_DIR = Path(__file__).parent.resolve()
README_FILE = BASE_DIR / "README.md"


long_description = ""

if README_FILE.is_file():
    long_description = README_FILE.read_text(encoding="utf-8")


setuptools.setup(
    name="cryptofetch",
    version="1.2.2",
    description="CLI tool to fetch and view cryptocurrencies prices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codeswhite/cryptofetch",
    author="Max G",
    author_email="max3227@gmail.com",

    python_requires=">=3.8",

    packages=setuptools.find_packages(),

    include_package_data=True,

    install_requires=[
        "interutils",
        "prettytable",
        "requests",
    ],

    entry_points={
        "console_scripts": [
            "cryptofetch = cryptofetch:main",
        ],
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],

    keywords=[
        "crypto",
        "cryptocurrency",
        "cli",
        "bitcoin",
        "ethereum",
        "market",
        "terminal",
    ],

    project_urls={
        "Source": "https://github.com/codeswhite/cryptofetch",
    },
)
