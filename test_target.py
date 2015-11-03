#!/usr/bin/env python
import os
import time
def main():
    with open(os.path.expanduser("~/Desktop/wrappaconda.test.txt"),"w") as f:
        msg = time.asctime() + ":  Hello from Wr[App]-A-Conda!"
        print msg
        f.write(msg)
main()
