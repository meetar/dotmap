import os
import sys
import ogr
from shapely.geometry import Polygon
from random import uniform
import sqlite3
from globalmaptiles import GlobalMercator
import zipfile
from time import time

def make_ogr_point(x,y):
	return ogr.Geometry(wkt="POINT(%f %f)"%(x,y))

def get_bbox(geom):
	ll=float("inf")
	bb=float("inf")
	rr=float("-inf")
	tt=float("-inf")

	ch = geom.ConvexHull()
	if not ch:
		return None
	bd = ch.GetBoundary()
	if not bd:
		return None
	pts = bd.GetPoints()
	if not pts:
		return None

	for x,y in pts:
		ll = min(ll,x)
		rr = max(rr,x)
		bb = min(bb,y)
		tt = max(tt,y)
		
	return (ll,bb,rr,tt)

def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print ' Please enter y or n'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False
			
def unlock(filename):
	import commands
	import re
	PID = commands.getoutput("fuser %s"%filename)
	# get the id of the locking process and kill it
	PID = re.search('\d+$', PID).group(0)
	print "Killing PID: %s"%PID
	os.environ['DBLOCK'] = PID
	os.system("kill -9 $DBLOCK")
	# sometimes unlocking a file will delete it -
	# if it's still there, delete it manually
	if os.path.isfile(filename):
		os.system("rm %s*"%filename)

def main(input_filename, output_filename):
	print "Processing: %s - Ctrl-Z to cancel"%input_filename
	merc = GlobalMercator()

	# open the shapefile
	ds = ogr.Open( input_filename )
	if ds is None:
		print "Open failed.\n"
		sys.exit( 1 )

	lyr = ds.GetLayerByIndex( 0 )

	lyr.ResetReading()

	feat_defn = lyr.GetLayerDefn()
	field_defns = [feat_defn.GetFieldDefn(i) for i in range(feat_defn.GetFieldCount())]

	# look up the index of the field we're interested in
	for i, defn in enumerate( field_defns ):
		if defn.GetName()=="POP10":
			pop_field = i

	# set up the output file
	# if it already exists, ask for confirmation to delete and remake it
	if os.path.isfile(output_filename):
		if not confirm("  Database %s exists, overwrite?"%output_filename, False):
			return False
		else:
			os.system("rm %s"%output_filename)
	
	# if file removal failed, the file may be locked:
	# ask for confirmation to unlock it
	if os.path.isfile(output_filename):
		if not confirm("  Attempt to unlock database %s?"%output_filename, False):
			return False
		else:
			unlock(output_filename)
		# if it's still there, there's a problem, bail
		if os.path.isfile(output_filename):
			print "Trouble - exiting."
			sys.exit()
		else:
			print "Success - continuing:"

	conn = sqlite3.connect( output_filename )
	c = conn.cursor()
	c.execute( "create table if not exists people (x real, y real, quadkey text)" )
	
	n_features = len(lyr)

	for j, feat in enumerate( lyr ):
		if j%1000==0:
			conn.commit()
			if j%10000==0:
				print " %s/%s (%0.2f%%)"%(j+1,n_features,100*((j+1)/float(n_features)))
			else:
				sys.stdout.write(".")
				sys.stdout.flush()

		pop = feat.GetField(pop_field)

		geom = feat.GetGeometryRef()
		if geom is None:
			continue

		bbox = get_bbox( geom )
		if not bbox:
			continue
		ll,bb,rr,tt = bbox

		# generate a sample within the geometry for every person
		for i in range(pop):
			while True:
				samplepoint = make_ogr_point( uniform(ll,rr), uniform(bb,tt) )
				if geom.Intersects( samplepoint ):
					break

			x, y = merc.LatLonToMeters( samplepoint.GetY(), samplepoint.GetX() )
			tx,ty = merc.MetersToTile( x, y, 21)
			quadkey = merc.QuadTree( tx, ty, 21 )

			c.execute( "insert into people values (?,?,?)", (x, y, quadkey) )
	
	conn.commit()
	print "Finished processing %s"%output_filename

if __name__=='__main__':
	
	print "US CENSUS DOTMAP GENERATOR"

	# read "States" preferences file
	states = []
	try:
		statesfile = open("states", "rU") # rU = universal newline interpretation
	except IOError:
		print "Couldn't open the States file!"
		sys.exit()
	lines = (line.rstrip() for line in statesfile) # All lines including the blank ones
	lines = (line for line in lines if line) # Non-blank lines
	for line in lines:
		li=line.strip()
		if not li.startswith("#"):
			states.append(line.rstrip())
	statesfile.close()
	print "Downloading states: %s:"%states
	starttime=time()
	
	#for state in ['01','02','04','05','06','08','09','10','11','12','13','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','44','45','46','47','48','49','50','51','53','54','55','56']:
  
  	if confirm("Step 1: Download files, Continue?", True):
		# download all data from ftp://ftp2.census.gov/geo/tiger/TIGER2010BLKPOPHU/
		downloadlist=""
		for state in states:
			downloadlist+=" ftp://ftp2.census.gov/geo/tiger/TIGER2010BLKPOPHU/tabblock2010_%s_pophu.zip"%state
		os.system("wget -t 3 -c -P ../data/zips/ "+downloadlist)
	
	for state in states:
		
		zf = zipfile.ZipFile("../data/zips/tabblock2010_%s_pophu.zip"%state)
		print "\nUnzipping: ../data/zips/tabblock2010_%s_pophu.zip"%state

		# check if files are already extracted
		for each in zf.namelist():
		  if not os.path.exists("../tmp/"+each):
			print each
			zf.extract(each, "../tmp")
		main( "../tmp/tabblock2010_%s_pophu.shp"%state, "../data/people.%s.db"%state )

	if confirm("Next step: .csv conversion, Continue?", True):
		os.system("bash makecsv.sh")

	if confirm("Next step: sort and merge .csv files, Continue?", True):
		if os.path.exists("../data/people.csv"):
			if confirm("File exists: people.csv, overwrite?", True):
				os.system("rm ../data/people.csv")
				if os.path.isfile("../data/people.csv"):
					if not confirm("  Could not delete, attempt to unlock?", False):
						print "Exiting"
						sys.exit()
					else:
						unlock("../data/people.csv")
					# if it's still there, there's a problem, bail
					if os.path.isfile("../data/people.csv"):
						print "Trouble - exiting."
						sys.exit()
					else:
						print "Success - continuing:"
						
				subprocesses.call("bash", "bashsort.sh")

	numstates=len(states)
	plural = "" if states == 1 else "s"
	totaltime=(time()-starttime)/60
	
	print "COMPLETED - Processed %s state%s in %.2f minutes"%(numstates, plural, totaltime)
	print "Next step, tile generation:"
	print " - Edit zoomlevels /lib/Processing/dotmap/data/zoomlevel"
	print " - Run /lib/Processing/dotmap/dotmap.pde in Processing"
	print " - view tiles in /index.html!"
