ifort 	..\libs\cgnsdll.lib^
	..\libs\iriclib.lib ^
	..\src\Uchannel_gen.f90 /MD -o Uchannel_gen.exe

del *.obj 
del *.mod 

