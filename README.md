dotmap
=========
An attempt to replicate Brendan Martin-Anderson's US Census Dotmap:
http://bmander.com/dotmap/index.html

The process described here is missing some pieces:
http://bmander.com/dotmap/methods.html

So I filled in some gaps and collected the files here. Additionally, getting all the python libraries can be tricky sometimes, so this repo includes a virtual machine (VM), which is like a cleanroom work environment in which to run the code.

Massive thanks to <https://github.com/robert-chiniquy/> for his help with this.

the process
-----------
US Census data is available down to the level of the "census block" – in cities these often correlate to city blocks, but elsewhere they may be delineated by other features. (More reading: http://en.wikipedia.org/wiki/Census_block)

Inside the bin/ directory are some scripts to automate the data-processing:
- **makedots.py** accesses the census data and gets the shape of each block and the number of people recorded as living there. Then it randomly places one dot for each person in the block shape, saving each dot's position as a latitude/longitude pair in a sqlite3 .db database file.
- **makecsv** converts each .db to a .csv (comma-separated values) file.
- **bashsort.sh** sorts all the .csv files and joins them into one .csv called people.csv. If you process all 51 states+DC, the resulting file is 17gb.

The Processing sketch (lib/Processing/dotmap/dotmap.pde) turns people.csv into tiled .png files.

requirements
------------

Using the VM, which automatically installs everything except Processing:
- VirtualBox (<https://www.virtualbox.org/>)
- Vagrant (<http://www.vagrantup.com/>)

For the manual method:
- Python 2.7
- Sqlite3
- The Python GDAL bindings (<http://pypi.python.org/pypi/GDAL/>)
- Other libraries depending on your machine's configuration.

Either way, you'll need:
- Processing (http://processing.org/)
- Lots and lots of memory and drive space if you want to render the whole map, less for only pieces. I rendered the whole map up to mid-level resolution, and that took 30GB of virtual memory and about 30GB of drive space.

setup
-----

Install the applications required above, depending on your method of choice.

Clone this repo in the directory of your choice:

    git clone git://github.com/meetar/dotmap.git
A directory called "dotmap" will be created.

**For the VM way:**  
Go to the dotmap directory and start the VM:

    cd dotmap
    vagrant up
...that takes a few minutes on my machine. Then:

Connect to the VM with ssh, either with an app like PuTTY or through the command line:

    ssh vagrant@127.0.0.1 -p 2222
    password: vagrant
    
Then change to the shared directory in the VM, which is the same as your local project directory:

    cd /vagrant
There you should see the files from this repo.

**For the manual method:**  
You're on your own.

instructions
------------
A preferences file "bin/states" contains a list of the states and their associated numbers, according to the US Census zipfiles. By default, only Alabama is uncommented - uncomment any others you'd like to include in your map. Uncommenting all the states will cause makedots.py to download and process about 17gb of files and could take many hours.

Then, go to the binaries dir and run makedots.py:

    cd bin
    python makedots
This will ask your permission to do a few things, in sequence:
 - Download and process the data for each state listed in "states", making a lot of .db files
 - Run 'bash makecsv.sh' to extract all the data from the .db files into a lot of .csv files
 - Run 'bash bashsort.sh' to sort all the .csv files and combine them into "people.csv"

Once the files are processed, it's time to generate the tiles!
- Open the Processing sketch: /lib/processing/dotmap/dotmap.pde
- Set the zoomlevels you want to render in the zoomlevel file: /lib/processing/dotmap/data/zoomlevel
- Add one level per line, from 4-14.
 
A note about zoomlevels: Level 4 is the widest view. Level 14 is the highest level, and shows individual neighborhoods. Higher levels seem to take about twice as much time to render as the level below them. Here are the times each level took for me:
 - Level 4: 30 minutes
 - Level 5: 1 hour
 - Level 6: 2 hour
 - Level 7: 4 hour
 - Level 8: 8 hours
 - Level 9: 16 hours
...I stopped there. Following this math, using this method, Level 14 could take 3 weeks.

Lastly, /index.html will display the tiles using Google JavaScript mapping API! You can watch the tiles fill in as they finish rendering if you zoom in and out.

When you're done with your virtual machine, be sure to turn it off by running `vagrant destroy`, the same way you ran `vagrant up`.

Good luck!  
<http://twitter.com/meetar>  
<m33tar@gmail.com>
