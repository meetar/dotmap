/* I, Brandon Martin-Anderson, release this into the public domain or whatever. */


BufferedReader reader;
double ll, bb, rr, tt;

float A = 1000.0;

GlobalMercator proj = new GlobalMercator();

class PersonPoint {
  double x, y;
  String quadnode;

  PersonPoint(String row) {
    String[] fields = split(row, ",");
    this.x = Double.parseDouble(fields[0])/A;
    this.y = Double.parseDouble(fields[1])/A;
    this.quadnode = fields[2];
  }

  void draw(PGraphics pg) {
    pg.point((float)this.x, (float)this.y);
  }
}

ArrayList people;

float pointWeight(int level) {
  switch(level) {
  case 4: 
    return 0.05333;
  case 5: 
    return 0.08;
  case 6: 
    return 0.12;
  case 7: 
    return 0.18;
  case 8: 
    return 0.27;
  case 9: 
    return 0.405;
  case 10: 
    return 0.6075;
  case 11: 
    return 0.91125;
  case 12: 
    return 1.366875;
  case 13: 
    return 2.0503125;
  case 14: 
    return 3.07546875;
  case 15: 
    return 4.61320312;
  case 16:
    return 6.9198046;
  case 17:
    return 10.37970;
  default: 
    return 0.0;
  }
}

void setup() {
  size(512, 512, P2D);
  smooth();

  String[] zoomlevels = loadStrings("zoomlevel");

  for ( int i=0; i<zoomlevels.length; i++ ) {

    int level = int(zoomlevels[i]);

    println( "loading..." );
    reader = createReader("../../../data/people.csv");
    try {
      String line;

      String quadkey = "";
      PGraphics pg = null;
      PVector tms_tile = null;
      
      int rown = 0;

      while (true) {
        line = reader.readLine();
        if (line==null || line.length()==0) {
          println( "file done" );
          break;
        }
        

        
        rown += 1;
        if( rown%100000==0 ){
          println( rown );
        }

        String[] fields = split(line, ",");
        float px = float(fields[0])/A;
        float py = float(fields[1])/A;
        String newQuadkey = fields[2].substring(0, level);
        
//          //only print out this quad:
//          if( !newQuadkey.substring(0,12).equals("032010110132") ){
//            continue;
//          }

        if ( !newQuadkey.equals( quadkey ) ) {
          //finish up the last tile
          if (pg!=null) {
            pg.endDraw();
            PVector gtile = proj.GoogleTile((int)tms_tile.x, (int)tms_tile.y, level);
						println( "../../../data/tiles/"+level+"/"+int(gtile.x)+"/"+int(gtile.y)+".png" );
            pg.save( "../../../data/tiles/"+level+"/"+int(gtile.x)+"/"+int(gtile.y)+".png" );
            println( "done" );
          }

          quadkey = newQuadkey;
          
          PVector google_tile = proj.QuadKeyToTileXY( newQuadkey );
          tms_tile = proj.GoogleTile( (int)google_tile.x, (int)google_tile.y, level );

          println( level+" "+tms_tile.x+" "+tms_tile.y );

          pg = createGraphics(512, 512, P2D);
          pg.beginDraw();
          pg.smooth();

          PVector[] bounds = proj.TileBounds( (int)tms_tile.x, (int)tms_tile.y, level );

          float tile_ll = bounds[0].x/A;
          float tile_bb = bounds[0].y/A;
          float tile_rr = bounds[1].x/A;
          float tile_tt = bounds[1].y/A;

          double xscale = width/(tile_rr-tile_ll);
          double yscale = width/(tile_tt-tile_bb);
          float scale = min((float)xscale, (float)yscale);

          pg.scale(scale, -scale);
          pg.translate(-(float)tile_ll, -(float)tile_tt);

          pg.strokeWeight(pointWeight(level));

          pg.background(255);
        }

        pg.point(px, py);
      }

      if (pg!=null) {
        pg.endDraw();
        PVector gtile = proj.GoogleTile((int)tms_tile.x, (int)tms_tile.y, level);
        pg.save( "../../../data/tiles/"+level+"/"+int(gtile.x)+"/"+int(gtile.y)+".png" );
				println( "../../../data/tiles/"+level+"/"+int(gtile.x)+"/"+int(gtile.y)+".png" );

        //println( "done" );
      }
    } 
    catch (IOException e) {
      //e.printStackTrace();
    }
  }
  println( "Completed!" );
}

void draw() {
}
