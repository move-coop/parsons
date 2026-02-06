SPHINXOPTS    = -a
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = Parsons
SOURCEDIR     = .
BUILDDIR      = _build

# Helper to clean up the multiversion output
clean:
	rm -rf $(BUILDDIR)
	rm -rf html/

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

build_docs:
	# Ensure branches exist or are updated
	git --git-dir ../.git --work-tree .. branch -f latest
	git --git-dir ../.git --work-tree .. branch -f stable $$(git tag -l --sort=creatordate | tail -1) || git --git-dir ../.git --work-tree .. branch -f stable latest

	# Build all versions
	rm -rf html/
	sphinx-multiversion "$(SOURCEDIR)" html
	cp ./index-redirect.html html/index.html

linkcheck:
	$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)

.PHONY: help Makefile build_docs linkcheck clean

# Catch-all
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
