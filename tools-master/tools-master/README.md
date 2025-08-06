# tools

Library of tools for CFD analyses with SU2.

- Construct2D: a software for the grid generation around airfoils. Structured O-type and C-type grids.
- c2d2su2: an executable for converting grids form .p3d (structured) to .su2 (unstructured) formats.
- su2story.py: a script to show the convergence istory of a CFD simulation with SU2.

  
sudo apt install 2to3
sudo apt install python3-pip
pip3 install numpy matplotlib scipy pandas 

siccome stiamo sulla WSL, per visualizzare le immagini fare il forwarding del plot al PC con: export DISPLAY=:0