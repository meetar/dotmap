cd ../data/
cat *.csv | awk -F',' '{print $3"_&_"$0}' | sort | sed -e 's/.*_&_//g' > people.csv