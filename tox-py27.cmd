call "%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Common\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat" x86
cd c:\projects\hypua2jamo
c:\python27\scripts\virtualenv .
call scripts\activate
pip install -U setuptools pip tox
tox -e py27
