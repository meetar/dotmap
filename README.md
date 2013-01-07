dotmap
=========
An attempt to replicate 
http://bmander.com/dotmap/index.html

fleshing out the process described here 
http://bmander.com/dotmap/methods.html

but including a VM.

The eventual goal:

To run: install VitrualBox and Vagrant, clone this to a project directory, and download all these zips to a subdirectory named "zips":
ftp://ftp2.census.gov/geo/tiger/TIGER2010BLKPOPHU/

Then, from the project directory, run "vagrant up". This should load the virtual machine and all dependencies, run the code, and generate the image files.

Later: serving.

Requirements: 16gb free space
