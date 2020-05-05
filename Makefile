define ALL
	update-requirements
endef
ALL:=$(shell echo $(ALL))  # to remove line-feeds

define REQUIREMENTS_FILES
	requirements/dev.txt
	requirements/docs.txt
	requirements/lint.txt
	requirements/test.txt
	requirements/site.txt
	requirements.txt
endef
REQUIREMENTS_FILES:=$(shell echo $(REQUIREMENTS_FILES))

define REQUIREMENTS_IN
	requirements.in
endef
REQUIREMENTS_IN:=$(shell echo $(REQUIREMENTS_IN))

define REQUIREMENTS_IN_SITE
	requirements.in
	requirements/site.in
endef
REQUIREMENTS_IN_SITE:=$(shell echo $(REQUIREMENTS_IN_SITE))

define REQUIREMENTS_IN_TEST
	requirements/setup.in
	requirements/test.in
	requirements.in
endef
REQUIREMENTS_IN_TEST:=$(shell echo $(REQUIREMENTS_IN_TEST))

define REQUIREMENTS_IN_LINT
	requirements/setup.in
	requirements/lint.in
endef
REQUIREMENTS_IN_LINT:=$(shell echo $(REQUIREMENTS_IN_LINT))

define REQUIREMENTS_IN_DOCS
	requirements/docs.in
	requirements.in
endef
REQUIREMENTS_IN_DOCS:=$(shell echo $(REQUIREMENTS_IN_DOCS))

define REQUIREMENTS_IN_DEV
	requirements/setup.in
	requirements/dev.in
	requirements/docs.in
	requirements/lint.in
	requirements/test.in
	requirements/site.in
	requirements.in
endef
REQUIREMENTS_IN_DEV:=$(shell echo $(REQUIREMENTS_IN_DEV))

offline?=0

ifeq (1,$(offline))
PIP_NO_INDEX:=--no-index
endif

FIND_LINKS:=
VENV	:= . bin/activate &&


.PHONY: all
all: $(REQUIREMENTS_FILES) update-requirements

.PHONY: update-requirements
update-requirements: .pip-sync
.pip-sync: requirements/dev.txt
	$(VENV) pip-sync $(FIND_LINKS) $(PIP_NO_INDEX) $^
	$(VENV) pip freeze > $@.tmp && mv $@.tmp $@

requirements.txt: $(REQUIREMENTS_IN)
	$(VENV)	pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV)	pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@ -w virtualenv_support

requirements/site.txt: $(REQUIREMENTS_IN_SITE)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/test.txt: $(REQUIREMENTS_IN_TEST)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/lint.txt: $(REQUIREMENTS_IN_LINT)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/docs.txt: $(REQUIREMENTS_IN_DOCS)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

requirements/dev.txt: $(REQUIREMENTS_IN_DEV)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^
	$(VENV) pip wheel $(FIND_LINKS) $(PIP_NO_INDEX) --no-deps -r $@

.PHONY: bootstrap-virtualenv
bootstrap-virtualenv.py: requirements.txt bootstrap-virtualenv.in
	python setup.py virtualenv_bootstrap_script -o $@ -r $<


.PHONY: notebook
notebook:
	$(VENV)	jupyter notebook --notebook-dir=notebooks

.PHONY: cythonize
cythonize:	src/hypua2jamo/_cython2.c \
		src/hypua2jamo/_cython3.c

src/hypua2jamo/_cython2.c: src/hypua2jamo/_cython.pyx
	$(VENV) cython $< -o $@ -2
src/hypua2jamo/_cython3.c: src/hypua2jamo/_cython.pyx
	$(VENV) cython $< -o $@ -3

.PHONY: test
test: requirements/test.txt cythonize
	$(VENV) tox -e py38
	$(VENV) coverage combine
	$(VENV) coverage report
	@mkdir -p build
	@cat	.benchmark.csv.* >	build/benchmark.csv
	@rm  -f	.benchmark.csv.*
	@cat 				build/benchmark.csv

.PHONY: test-report
test-report:
	$(VENV) coverage xml
	$(VENV) coverage html


.PHONY: data
data:
	$(VENV) ktug-hanyang-pua -vvv -m table data/hypua2jamocomposed.txt	-F binary -o src/hypua2jamo/p2jc.bin
	$(VENV) ktug-hanyang-pua -vvv -m table data/hypua2jamodecomposed.txt	-F binary -o src/hypua2jamo/p2jd.bin
	$(VENV) ktug-hanyang-pua -vvv -m table data/jamocompose.map	-S	-F binary -o src/hypua2jamo/c2d.bin
	$(VENV) ktug-hanyang-pua -vvv -m tree data/hypua2jamocomposed.txt	-F binary -o src/hypua2jamo/jc2p.bin
	$(VENV) ktug-hanyang-pua -vvv -m tree data/hypua2jamodecomposed.txt	-F binary -o src/hypua2jamo/jd2p.bin
	$(VENV) ktug-hanyang-pua -vvv -m tree data/jamocompose.map	-S	-F binary -o src/hypua2jamo/d2c.bin
