#!/bin/sh

git stash
git checkout -b latest
git checkout $(git tag -l --sort=creatordate |tail -1)
git checkout -b stable
git stash apply

sphinx-multiversion . html
cp ./index-redirect.html html/index.html