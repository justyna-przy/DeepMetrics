from setuptools import setup, find_packages

setup(
    name="metric_aggregator_sdk",
    version="0.1.0",
    description="A resilient SDK for aggregating and uploading device snapshots. Part of my ISE Context of the Code project.",
    author="Justyna Przyborska",
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
        "dataclasses-json",
    ],
    python_requires=">=3.7",
)
