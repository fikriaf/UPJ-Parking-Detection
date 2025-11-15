# Quick Test Reference Card

## 🚀 Quick Start (3 Steps)

### 1. Start Server
```bash
cd backend
uvicorn main:app --reload
```

### 2. Run Tests
```bash
# Windows
run_tests.bat

# Linux/Mac
./run_tests.sh
```

### 3. Check Results
- Console output shows pass/fail status
- Test images: `test_data/images/`
- Visualizations: `uploads/best_frames/`

## 📋 Test Files

| File | Purpose | Run Command |
|------|---------|-------------|
| `test_calibration.py` | Basic API tests | `python test_calibration.py` |
| `test_e2e_parking.py` | Full E2E tests | `python test_e2e_parking.py` |
| `generate_test_report.py` | Visual report | `python generate_test_report.py` |

## ✅ What Gets Tested

- [x] Calibration CRUD operations
- [x] Empty space detection
- [x] Coordinate accuracy
- [x] Visualization generation
- [x] Multiple parking scenarios
- [x] Edge cases & error handling
- [x] API authentication
- [x] Data validation

## 📊 Expected Output

```
✅ PASS: Server Health
✅ PASS: Create Calibration
✅ PASS: Get Calibration
✅ PASS: Upload Frame
✅ PASS: Verify Empty Spaces
✅ PASS: Verify Coordinates
✅ PASS: Verify Visualization
✅ PASS: Multiple Scenarios
✅ PASS: Edge Cases

Pass Rate: 100.0%
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Server not running | `uvicorn main:app --reload` |
| API key error | Check `ADMIN_API_KEY` in `.env` |
| Model not found | Ensure `models/best.pt` exists |
| MongoDB error | Verify `MONGODB_URL` in `.env` |

## 📚 Documentation

- **Detailed Guide**: [TEST_GUIDE.md](TEST_GUIDE.md)
- **Implementation Summary**: [TESTING_SUMMARY.md](TESTING_SUMMARY.md)
- **Main README**: [README.md](README.md)

## 🎯 Test Coverage

All 5 requirements from specification:
1. ✅ Admin calibration configuration
2. ✅ Distance calculation
3. ✅ Parking space validation
4. ✅ Calibration API endpoints
5. ✅ Result visualization

## 💡 Tips

- Tests create synthetic images automatically
- No manual image preparation needed
- Tests clean up after themselves
- Safe to run multiple times
- Can run individual test files

## 🔄 CI/CD Integration

```bash
# Start server in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 5

# Run tests
python test_e2e_parking.py

# Exit with test result
exit $?
```
