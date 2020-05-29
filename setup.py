from distutils.core import setup

setup(
    name="OpenCDN-client",
    packages=["open_cdn"],
    version="0.10",
    license="gpl-3.0",
    description="A client to communicate with the OpenCDN backend.",
    author="AdriBloober",
    author_email="adribloober@adribloober.wtf",
    url="https://github.com/AdriBloober/OpenCDN-client",
    keywords=["client", "api", "opencdn", "open-cdn"],
    install_requires=["requests", "pycryptodome"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GPL-3.0",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
