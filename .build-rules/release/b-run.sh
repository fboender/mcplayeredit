#!/bin/sh

VERSION=$1

if [ -z $VERSION ]; then
	echo "Version required for this build rule" >&2
	exit
fi

if [ -d 'releases' ]; then
	rm -rf releases
fi

# Create the release directory structure.
mkdir releases
mkdir releases/mcplayeredit-$VERSION

# Copy the source to the release directory structure.
cp HISTORY.txt releases/mcplayeredit-$VERSION/
cp LICENSE.txt releases/mcplayeredit-$VERSION/
cp README.txt releases/mcplayeredit-$VERSION/
cp mcplayeredit.py releases/mcplayeredit-$VERSION/
cp mcplayeredit_icon.png releases/mcplayeredit-$VERSION/
cp -r lib releases/mcplayeredit-$VERSION/

# Remove some files / directories we don't want in the release.
find releases/ -name ".svn" -type d -print0 | xargs -0 /bin/rm -rf
find releases/ -name "*.pyc" -type f -print0 | xargs -0 /bin/rm -rf

# Bump version numbers
cd releases/mcplayeredit-$VERSION/
sed -i "s/%%VERSION%%/$VERSION/g" README.txt HISTORY.txt mcplayeredit.py 
cd ../..

# Create package releases.
cd releases
tar -czf mcplayeredit-$VERSION.tar.gz mcplayeredit-$VERSION/
zip -q -r mcplayeredit-$VERSION.zip mcplayeredit-$VERSION/
cd ..

# Clean up
#rm -rf releases/mcplayeredit-$VERSION
