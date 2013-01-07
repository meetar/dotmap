import os
import sys
import ogr
from shapely.geometry import Polygon
from random import uniform
import sqlite3
from globalmaptiles import GlobalMercator
import zipfile

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


def main(input_filename, output_filename):
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
		conn = sqlite3.connect( output_filename )
		c = conn.cursor()
		c.execute( "create table if not exists people (x real, y real, quadkey text)" )
		
		n_features = len(lyr)

		for j, feat in enumerate( lyr ):
				if j%1000==0:
						conn.commit()
						print "%s/%s (%0.2f%%)"%(j+1,n_features,100*((j+1)/float(n_features)))

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

if __name__=='__main__':
		#for state in ['01','02','04','05','06','08','09','10','11','12','13','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','44','45','46','47','48','49','50','51','53','54','55','56']:

		#for state in ['44','45','46','47','48','49','50','51','53','54','55','56']:
		for state in ['02']:
				print "state:%s"%state
				zf = zipfile.ZipFile("../data/tabblock2010_"+state+"_pophu.zip")
				# check if files are already extracted
				for each in zf.namelist():
					print each
					if not os.path.exists("../tmp/"+each):
						zf.extract(each, "../tmp")
					#else:
				#main( "../tmp/tabblock2010_"+state+"_pophu.shp", "people.db" )
				main( "../tmp/tabblock2010_"+state+"_pophu.shp", "../data/out/people.msort."+state+".db" )
				