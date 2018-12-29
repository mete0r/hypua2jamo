call "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.cmd" /Release /x86
cd c:\projects\hypua2jamo
c:\python27\scripts\virtualenv .
call scripts\activate
pip install -U setuptools pip tox
tox -e py34
