#!/bin/bash

if [ -n "$1" ]; then
	python3 executables/cli.py $1
else
	python3 executables/cli.py simulate
fi
