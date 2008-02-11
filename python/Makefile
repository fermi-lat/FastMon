
all:	
	echo "Targets are: builddoc, clean, cleandoc, cleanall, viewdoc"

builddoc:
	python updateDoxCfg.py
	doxygen doxygen.cfg

clean:
	rm -rf *~ .*~ *.pyc *.pyo	
	rm -rf pGEMcontribution.py pTKRcontributionIterator.py
	rm -rf pCALcontributionIterator.py pAEMcontributionIterator.py
	rm -rf *_test.* 

cleandoc:
	rm -rf doc

cleanall:
	make clean
	make cleandoc

viewdoc:
	htmlview ./doc/html/index.html &
