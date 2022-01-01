@echo off

REM Can't use -OO because it removes docstrings and PLY depends on them.
%LOCALAPPDATA%\Programs\Python\Python39\python.exe %LOCALAPPDATA%\Programs\Python\Python39\Scripts\cxfreeze.exe ..\s2s.py --icon=s2s_logo.ico