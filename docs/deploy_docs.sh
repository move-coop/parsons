#!/bin/sh

git checkout -b latest
git stash
git checkout $(git tag -l --sort=creatordate |tail -1)
git checkout -b stable
git checkout master

sphinx-multiversion . html
cp ./index-redirect.html html/index.html