
all:	
	echo "Targets are: doc, clean, cleandoc, cleanall, view"

doc:
	doxygen doxygen.cfg

cleandoc:
	rm -rf doc

clean:
	rm -rf *~ .*~ *.pyc *.pyo	
	rm -rf pGEMcontribution.py pTKRcontributionIterator.py
	rm -rf pCALcontributionIterator.py pAEMcontributionIterator.py
	rm -rf *_test.* 

cleanall:
	make clean
	make cleandoc

view:
	htmlview ./doc/html/index.html &
