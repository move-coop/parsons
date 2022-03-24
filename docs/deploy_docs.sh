#!/bin/sh

git branch latest
git branch stable $(git tag -l --sort=creatordate |tail -1)

sphinx-multiversion . html
cp ./index-redirect.html html/index.html