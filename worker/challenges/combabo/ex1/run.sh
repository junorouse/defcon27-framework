#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd $DIR # change path to its path

stdbuf -i0 -o0 -e0 python solve.py
# python solve.py
