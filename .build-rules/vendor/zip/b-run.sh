#!/bin/sh

ZIP_HAS=`which zip`
if [ -z "$ZIP_HAS" ]; then
	echo "zip not installed" >&2
	exit 1
fi
