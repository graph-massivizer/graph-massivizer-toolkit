#!/bin/bash

if [ "-as" = "$1" ]; then
	docker buildx build --platform=linux/amd64 -t gm/runtime:latest .
else
	docker build -t gm/runtime:latest .
fi

