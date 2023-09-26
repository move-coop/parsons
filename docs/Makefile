# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -a
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = Parsons
SOURCEDIR     = .
BUILDDIR      = .

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

deploy_docs:
	git branch latest
	git branch stable $$(git tag -l --sort=creatordate | tail -1)
	sphinx-multiversion . html
	cp ./index-redirect.html html/index.html

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
