@echo off
echo Fixing pkuseg installation...

REM Clone the repository
git clone https://github.com/lancopku/pkuseg-python.git pkuseg_tmp
cd pkuseg_tmp

REM Install build dependencies
pip install cython numpy setuptools wheel

REM Delete pre-generated C++ files to force Cython regeneration
echo Deleting pre-generated C++ files...
del /s /q pkuseg\*.cpp
del /s /q pkuseg\*.c
del /s /q pkuseg\*.h

REM Install from source
echo Installing pkuseg...
pip install --no-build-isolation .

REM Cleanup
cd ..
rmdir /s /q pkuseg_tmp

echo pkuseg fixed! Now run: pip install -r requirements.txt
pause
