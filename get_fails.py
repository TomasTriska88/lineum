import pytest

class P:
    def pytest_runtest_logreport(self, report):
        if report.when == 'call' and report.failed:
            print("---")
            print(f"FAIL: {report.nodeid}")
            if report.longreprtext:
                print(report.longreprtext.splitlines()[-1])

pytest.main(['-q', '--disable-warnings', 'tests/test_wave_core.py', 'portal/src/lib/data/routing_backend/test_lab_api.py'], plugins=[P()])
