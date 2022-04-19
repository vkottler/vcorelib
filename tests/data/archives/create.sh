#!/bin/bash

REPO=`git rev-parse --show-toplevel`
CWD=$REPO/tests/data/archives
pushd $CWD >/dev/null

SRC=sample

# Ensure all archives are re-created.
rm -rf $SRC.*

# Create an uncompressed archive.
tar cf $SRC.tar $SRC

# Create a 'gzip' archive.
tar czf $SRC.tar.gz $SRC

# Create a 'bzip2' archive.
tar cjf $SRC.tar.bz2 $SRC

# Create an 'lzma' archive.
tar --lzma -cf $SRC.tar.lzma $SRC

# Create a 'ZIP' archive.
zip -r $SRC.zip $SRC

popd >/dev/null
