#!/bin/bash

set -x
set -e

# copy to site-packages
cp wrappaconda.py $SP_DIR/

# copy launcher
cp bin/wrappaconda $PREFIX/bin/

exit
