@echo off
REM Parking Calibration System - Test Runner for Windows
REM This script runs the end-to-end tests

echo ========================================
echo Parking Calibration System - Test Runner
echo ========================================
echo.

REM Check if server is running
echo Checking if server is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Server is not running!
    echo.
    echo Please start the server first:
    echo   cd backend
    echo   uvicorn main:app --reload
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo Server is running!
echo.

REM Run basic API tests
echo ========================================
echo Running Basic API Tests...
echo ========================================
python test_calibration.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some basic tests failed
    echo.
)

echo.
echo.

REM Run comprehensive E2E tests
echo ========================================
echo Running End-to-End Tests...
echo ========================================
python test_e2e_parking.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: End-to-end tests failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo All tests completed!
echo ========================================
echo.
echo Check the following:
echo   - Test output above
echo   - Generated images in test_data/images/
echo   - Visualization images in uploads/best_frames/
echo.
pause
