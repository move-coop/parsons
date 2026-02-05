# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -a
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = Parsons
SOURCEDIR     = .
# Change BUILDDIR to a subfolder to avoid Sphinx registration/conflict issues
BUILDDIR      = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

deploy_docs:
	git --git-dir ../.git --work-tree .. branch -f latest
	git --git-dir ../.git --work-tree .. branch -f stable $$(git tag -l --sort=creatordate | tail -1) || git --git-dir ../.git --work-tree .. branch -f stable latest
	rm -rf html/
	sphinx-multiversion . html
	cp ./index-redirect.html html/index.html

linkcheck:
	$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)

.PHONY: help Makefile deploy_docs linkcheck

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
