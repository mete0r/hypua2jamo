PREFIX := ../..
CFLAGS := -Wall -fPIC

p2j4.a: p2jc4.o p2jd4.o
	ar rc $@ $^
p2jc4-table.h p2jd4-table.h:
	python data2c.py

p2jc4.o: p2jc4.c p2jc4-table.h
p2jd4.o: p2jd4.c p2jd4-table.h

.PHONY: clean
clean:
	rm -f *.a *.o
	rm -f *-table.h


.PHONY: install
install: install-lib
install-lib: p2j4.a
	[ -d $(PREFIX)/lib ] || mkdir -p $(PREFIX)/lib
	/usr/bin/install -t $(PREFIX)/lib $^

.PHONY: uninstall
uninstall:
	rm -f $(PREFIX)/lib/p2j4.a
