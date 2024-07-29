import os

if 'VIRTUAL_ENV' in os.environ:
    print(f"Inside a virtual environment at{os.environ['VIRTUAL_ENV']}")
else:
    print("Not inside a virtual environment")    