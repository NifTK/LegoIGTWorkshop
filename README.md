LEGO Mindstorms IGT Workshop
============================

Setup
----------------------------

This workshop is designed to work with the  
[LEGO Mindstorms EV3 kit](https://shop.lego.com/en-GB/LEGO-MINDSTORMS-EV3-31313)
and a standard 
[box of lego bricks](https://shop.lego.com/en-GB/LEGO-Large-Creative-Brick-Box-10698). 

This is an updated version of the 
[workshop](https://na-mic.org/wiki/LEGO_IGT_and_Medical_Robotics_Tutorial)
originally developed by the National Alliance for Medical Imaging Computing
which used the previous generation LEGO Mindstorms.

The phantom hasn't changed from the previous workshop, so you can use the same 
[inststructions](https://na-mic.org/w/images/0/0d/LEGOIGTAndMedicalRoboticsTutorial_PhantomAssemblyInstructions.pdf)
to construct it. Note that the newer 
[box of lego bricks](https://shop.lego.com/en-GB/LEGO-Large-Creative-Brick-Box-10698)
does not have the same bricks as the old one, so substitutions have to be made.

We are using the 3rd party [ev3dev](http://www.ev3dev.org/) operating system 
to program the EV3 brick. If you are using a kit that has already been used for 
this workshop it most likely already has that OS installed. However, if not 
follow the instructions [here](http://www.ev3dev.org/docs/getting-started/).

The brick must be connected to the internet somehow, both to download the script
and to communicate with the PC. Since we don't need mobility, there is no reason
to set up a wireless connection, and the 
[USB connection](http://www.ev3dev.org/docs/tutorials/connecting-to-the-internet-via-usb/)
should be fine.

To get the script on the EV3 brick you can either clone this repository, or just
copy and paste the contents of the `lego-workshop.py` file into a new file on 
the EV3. If you do, make sure to mark the new file as executable.

For the PC, download [Slicer](https://www.slicer.org/). This workshop has been 
tested with [version 4.8.1](http://slicer.kitware.com/midas3/folder/4989)
but it should work with similar versions. 

Basic Tutorial: Image Guided Therapy
------------------------------------

![Warning about using Slicer for clinical use](Screenshots/01-ClinicalWarning.png)

Open the Application Settings by clicking `Edit->Application Settings`:

![Edit->Application Settings](Screenshots/02-AppSettings.png)

Go to the `Modules` tab:

![List of Module Paths](Screenshots/03-ModulesEmpty.png)

Add a path under `Additional Module Paths` which points to the folder named 
LegoWorkshop in this repository:

![Choose Directory](Screenshots/04-ChooseDirectory.png)

Now that directory will be in the list:

![List of Module Paths](Screenshots/05-ModulesFull.png)

This will require a reboot of the program to take effect:

![Restart Required](Screenshots/06-RestartRequired.png)

To use the module, load it from the Modules menu:

![Choosing LEGO Module](Screenshots/07-SelectingLEGOModule.png)

Make sure that under `LegoWorkshop - Configuration` 
the server address matches the address of your brick, (probably `ev3dev.local`).
If `ev3dev.local` doesn't work, get the IP of the EV3 from the menu 
`WirelessAndNetowrks->AllNetowrkConnections->[Wired or other]->IPv4`.
If the module loaded correctly it should look something like the following:

![Loaded Module](Screenshots/08-LoadedLEGOModule.png)

Download the 
[CT volume of the LEGO phantom](http://wiki.na-mic.org/Wiki/images/6/69/000003.SER.zip)
and extract it somewhere. Now open that data with `File->Add Data` and point to 
the first file in the series:

![File->Add Data](Screenshots/09-OpenFile.png)

Show additional options:

![Additional Options](Screenshots/10-ShowOptions.png)

Uncheck the `Single File` box:

![Not Single File](Screenshots/11-NotSingleFile.png)

Click OK. Now you should see the CT scan of a LEGO phantom:

![Not Single File](Screenshots/12-LEGOScanLoaded.png)

Then add a Fiducial to the point you want to target by clicking on the icon with
the red dot and blue arrow:

![Select Feducial](Screenshots/13-SelectFeducial.png)

Then click somewhere you want the robot to probe, and then choose the feducial 
namespace (`F`) and that position will displayed on the list:

![Feducial List](Screenshots/14-FeducialList.png)

Then choose which point(s) you want the robot to 'probe' by ticking the box next
to them. When you are ready (and assuming you are running `lego-workshop.py`), 
press the `Go` button:

![Send Go Command](Screenshots/15-SendCommand.png)

This should make the robot move!

Advanced Tutorial: Manual Registration
--------------------------------------

A calibration of the robot to the phantom was already programmed into the Slicer 
module, but if you want to move the robot to somewhere else around the phantom,
while still having it within range of the injector, you can perform a manual 
registration. This is done by selecting at least 3 feducials and getting 
measurements of how those relate to the robot in the real world. Once you have
your points ticked, press the `Replace Calibration Points` button:

![Send Go Command](Screenshots/21-ReplaceCalibration.png)

This will bring the points up to the table, but you will notice that the joint 
values are empty. To fill those we will use another python script that outputs 
the joint values without running the motors. It is called `lego-debug.py` and 
should be run through ssh so that you can see the output. Move the robot to 
point towards the calibration points you chose (keeping in mind that they need 
to correspond 1:1), and fill in the values. 

Note that the inject motor's encoder is spotty, and sometimes doesn't work so 
it is currently not implemented (`lego-debug.py` will either show 0 or a huge number)
so you have to measure the distance from the orange circle of the upright large motor 
to your calibration point in millimeters, and that value will be `Dst`.

```
robot@ev3dev:~/lego-igt-workshop$ Python/lego-debug.py 
Press the touch sensor to read the motor positions
WARNING! The inject motor does not seem to work, you will have to measure that manually

Dst Azm Elv
-1467 38 44
-1467 38 44
```

Enter those numbers into the table:

![Enter Joint Values](Screenshots/22-EnterCalibration.png)

The press the `Rerun Calibration` button to get a new calibration:

![Rerun Calibration](Screenshots/23-RerunCalibration.png)

Now you can test out your new calibration!

Note that if you think something is wrong you can set `Check_Calibration=True` in
`LegoWorkshop.py` and if you run Slicer from a terminal you can get the details of
the linear algebra, including the RMSE which (if you used more than 3 points) lets
you know how well the calibration points agree on a registration.

