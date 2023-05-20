from setuptools import find_packages, setup

setup(
    name="crs2rss",
    version="0.1",
    packages=find_packages(include=["crs2rss", "crs2rss.*"]),
    include_package_data=True,
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "crs2rss = crs2rss.cli:cli",
        ],
    },
)
