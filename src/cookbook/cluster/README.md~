# analyze_meta 

To run a shotgun-metagenome through the analysis (not amplicon):  

MAKE NEST  
1. Be sure you have run the file through a prep script built for this analysis [see ../prep_seq/README.md]  
2. Copy make_nest_HTC.sh.temp and make_nest_HTC.sub.temp to your project dir  
3. Remove the .temp extension from their names  
2. Fill out the make_nest_HTC.sh with your path to refpkgs and metagenomes [comments in script]  
4. Save the changes to make_nest_HTC.sh so that the make_nest_HTC.sub script will find it  
5. Check that the make_nest_HTC.sub script has the config you want, i.e., # of machines, ...  
6. Confirm that the .sh script is executable by others than yourself, "chmod 777 filename" [maybe find a better option as this is somewhat dangerous as commands go]  
7. Once you have modified both scripts run "condor_submit make_nest_HTC.sub" in your project dir  
8. Check that your script has made it to the cluster by using "condor_q -submitter your_username"  
9. Wait for it to complete......................  

DO NESTRUN  
1. Copy "pancakes.py" to your project dir  
2. Check that the pathways to "search.sh" and "search_place.sub" templates are correct  
3. Run "python pancakes.py"  
4. This should throw all the ./analysis dirs onto the cluster, check to confirm  
5. Wait for them to complete....................  

GRAB JPLACE  
1. Copy "extractalator.py" to your project dir  
2. Run "python extractalator.py"  
3. This will create a new dir called "place_files" in your project dir  
4. It will then populate the new dir with all the jplace files under './analysis'  

DAP  
buffering....  
