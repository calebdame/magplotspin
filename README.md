MagPlotSpin:
-
A GUI Interface to assign magnetic spins to molecular structures.

To be integrated into diffpy.magpdf (@benfrandsen) to facilitate spin assignment when implementing the program

Necessary libraries (not included as a standard module):
-
- diffpy/Structure
- numpy
- matplotlib
- PyQT5

Standard modules imported:
-
- os
- sys
- tkinter
- pickle

Instructions to run:
-
1. Place structure file (.cif file) in \_cif folder _(this is the default folder opened to load a .cif file - Files from elsewhere can be loaded once navigated to)_
2. Run run.py in conda environment with diffpy installed

Instructions to use:
- 
1. Select file either in \_cif folder or another folder
2. Decide which atoms can be selected, either individually or by atom type
3. In the viewer, assign the atoms with spins (press i in viewer to see controls)
4. In in popup, one can assign a spin to all the atoms selected and optionally include a non-unit magnitude or non-zero propagation vector
5. Upon closing the viewer by pressing close or escape, the spins, magnitudes, and propagation vectors are saved as a MagStructure Object (diffpy.magpdf) as mag_output.pkl
6. Read object into existing code with 

 <pre>with open('/path/to/mag_output.pkl', 'rb') as f:<br>
    mag = pickle.load(f)</pre>


