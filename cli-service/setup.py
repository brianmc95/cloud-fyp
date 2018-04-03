from setuptools import setup

setup(
    name="cloudService",
    version="1.0",
    py_modules=["cloudService"],
    install_requires=[
        "Click",
        "requests",
    ],
    entry_points="""
        [console_scripts]
        cloudService=cloudService:cli
    """,
)