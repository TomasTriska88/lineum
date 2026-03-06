import pytest
import io
import sys

def main():
    class CatchOutput:
        def __init__(self):
            self.output = []
        def write(self, s):
            self.output.append(s)
        def flush(self):
            pass

    c = CatchOutput()
    sys.stdout = c
    sys.stderr = c
    try:
        pytest.main(["routing_backend/test_lab_api.py", "-v", "--tb=short"])
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    with open("test_out.txt", "w", encoding="utf-8") as f:
        f.write("".join(c.output))

if __name__ == "__main__":
    main()
