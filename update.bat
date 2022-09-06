@echo off

IF EXIST %~dp0venv\ (
    echo VENV DIRECTORY EXISTS
) ELSE (
    echo VENV NOT EXIST 
    cd %~dp0
    python -m venv venv
    echo DIRECTORY CREATED
)

call %~dp0venv\Scripts\activate

python -m pip install -r requirements.txt
echo UPDATE SUCCESSFUL

pause