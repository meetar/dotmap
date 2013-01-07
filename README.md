dotmap
=========
An attempt to replicate Brendan Martin-Anderson's US Census Dotmap:
http://bmander.com/dotmap/index.html

The process described here is missing some pieces:
http://bmander.com/dotmap/methods.html

So I filled in some gaps and collected the files here. Additionally, getting all the python libraries can be tricky sometimes, so this repo includes a virtual machine, which is like a cleanroom work environment in which to run the code.

the process
-----------
US Census data is available down to the level of the "census block" – in cities these often correlate to city blocks, but elsewhere they may be delineated by other features. (More reading: http://en.wikipedia.org/wiki/Census_block)

Inside the bin/ directory are some scripts to automate the data-processing.

'makedots.py' accesses the census data and gets the shape of each block and the number of people recorded as living there. Then it randomly places one dot for each person in the block shape, saving each dot's position as a latitude/longitude pair in a sqlite3 .db database file.

'makecsv' converts each .db to a .csv (comma-separated values) file.

'bashsort.sh' sorts all the .csv files and joins them into one .csv called people.csv. If you process all 51 states+DC, the resulting file is 17gb.

The processing sketch (lib/Processing/dotmap/dotmap.pde) renders tiled .png files from the .csv.

And lastly, /index.html will display the tiles using Google JavaScript mapping API! You can watch the tiles fill in as they finish rendering if you zoom in and out.


requirements
------------

For the virtual machine way:
VirtualBox (https://www.virtualbox.org/)
Vagrant (http://www.vagrantup.com/)

OR - For the manual method:
Python 1.5
Sqlite3
The Python GDAL bindings (http://pypi.python.org/pypi/GDAL/)

Either way, you'll need:
Processing (http://processing.org/)
Lots and lots of memory and drive space if you want to render the whole map, less for only pieces. I only rendered up to mid-level resolution, and that took 30GB of virtual memory and 30GB of drive space.

setup
-----

Install the applications required above, depending on your method of choice.

Clone this repo in the directory of your choice:
    git clone git://github.com/meetar/dotmap.git
A directory called "dotmap" will be created.

For the virtual machine way:
Go to the dotmap directory
	cd dotmap
Start the VM
	vagrant up
...that takes a few minutes on my machine. Then:
Connect to the VM with ssh, either with an app like PuTTY or through the command line:
  ssh 127.0.0.1:8888
	user: vagrant
	password: vagrant
Then change to the shared directory in the virtual machine, which is the same as your project directory:
  cd /vagrant

For the manual method:
You're on your own.

instructions
------------
A file called "states" has a list of the states and their associated numbers, as according to the US Census zipfiles. Comment out or remove the states you'd like to process.

Then, go to the binaries dir:
    cd bin
And run makedots:
    python makedots
This will download and process each zipfile listed in "states", making a lot of .db files. Then:
	bash makecsv.sh
This will extract all the data from the .db files into a lot of .csv files. Then:
	bash bashsort.sh
This will sort all the .csv files and combine them into "people.csv".

Open the processing sketch:
	/lib/processing/dotmap/dotmap.pde
Set the zoomlevels you want to render in the zoomlevel file:
	/lib/processing/dotmap/dotmap.pde
Add one level per line, from 4-14. Level 4 is the lowest zoom level, aka satellite view. Level 14 is the highest level, and shows individual neighborhoods.

Higher levels seem to take about twice as much time to render as the level below them. Here are the times each level took for me:
Level 4: 30 minutes
Level 5: 1 hour
Level 6: 2 hour
Level 7: 4 hour
Level 8: 8 hours
Level 9: 16 hours
...I stopped there. Following this math, using this method, Level 14 could take 3 weeks. I don't know how he did it.

You may view the tiles as they render by opening this page:
	/index.html
	
When you're done with your virtual machine, be sure to turn it off with "vagrant destroy"

Good luck!
@meetar
m33tar@gmail.com