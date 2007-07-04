
all:	
	echo "Targets are: doc, clean, cleandoc, cleanall, view"

doc:
	doxygen doxygen.cfg

cleandoc:
	rm -rf doc

clean:
	rm -f *~ .*~ *.pyc *.pyo	
	rm -f pGEMcontribution.py pTKRcontributionIterator.py
	rm -f pCALcontributionIterator.py pAEMcontributionIterator.py

cleanall:
	make clean
	make cleandoc

view:
	htmlview ./doc/html/index.html &
