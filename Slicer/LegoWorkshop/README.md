Installation Guide
-----------------------

1.    Add pyserial to the Slicer python version with the following command:
```
./Slicer --launch ./bin/python-real -c "import pip; pip.main(['install', 'pyserial'])"
```
or something like this on windows
```
Slicer.exe --launch bin\python-real.exe -c "import pip; pip.main(['install', 'pyserial'])"
```
This is taken from https://discourse.slicer.org/t/slicer-python-packages-use-and-install/984/2

2.    Open 3DSlicer and go to Edit > Application Settings > Modules.

3.    Expand the box "Additional module paths:" by clicking the arrow on the right side. This shows the Add and Remove buttons

4.    Click Add and navigate to the directory where you downloaded the LegoWorkshop Module.

5.    After adding each module, Click Apply. Slicer wants to be reloaded.

6.    After reloading the modules should be listed under the "Modules:" list.

