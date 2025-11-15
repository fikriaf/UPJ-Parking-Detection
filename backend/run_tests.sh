#!/bin/bash
# Parking Calibration System - Test Runner for Linux/Mac
# This script runs the end-to-end tests

echo "========================================"
echo "Parking Calibration System - Test Runner"
echo "========================================"
echo ""

# Check if server is running
echo "Checking if server is running..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "ERROR: Server is not running!"
    echo ""
    echo "Please start the server first:"
    echo "  cd backend"
    echo "  uvicorn main:app --reload"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "Server is running!"
echo ""

# Run basic API tests
echo "========================================"
echo "Running Basic API Tests..."
echo "========================================"
python test_calibration.py
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Some basic tests failed"
    echo ""
fi

echo ""
echo ""

# Run comprehensive E2E tests
echo "========================================"
echo "Running End-to-End Tests..."
echo "========================================"
python test_e2e_parking.py
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: End-to-end tests failed"
    exit 1
fi

echo ""
echo "========================================"
echo "All tests completed!"
echo "========================================"
echo ""
echo "Check the following:"
echo "  - Test output above"
echo "  - Generated images in test_data/images/"
echo "  - Visualization images in uploads/best_frames/"
echo ""
