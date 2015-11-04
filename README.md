# Wr[App]-A-Conda
Generates an OS X app that wraps an Anaconda bundle.  The app can be configured
to run any binary from Anaconda's `bin` directory.

## Install
You can install wrappaconda via conda with:

    $ conda install -c https://conda.anaconda.org/nckz wrappaconda

The script can be invoked by entering:

    $ wrappaconda -h

Or just clone the repository:

    $ git clone https://github.com/nckz/wrappaconda.git
    $ wrappaconda/wrappaconda.py -h

## Example
To wrap the Jupyter console into a standalone app called "JupyterConsole", enter:

    $ wrappaconda -n JupyterConsole -t jupyter-qtconsole -p ipython-qtconsole

An example of how wrappaconda can be used to wrap a simple Qt app can be found
in the [RevAssign](https://github.com/nckz/RevAssign/blob/master/wrappaconda/wrappaconda.sh)
project. 
