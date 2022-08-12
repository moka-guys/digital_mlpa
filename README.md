# digital_mlpa
Scripts for supporting the digital MLPA service.
</br>
</br>
The output from the digital MLPA software provides results for all the probe regions covered.
</br>
To prevent incidental findings, these scripts have been created to filter the results based on a pan number per patient

# digital_mlpa_filtering.py 

This script:
 1) Imports unfiltered digital MLPA data from an xls
 2) Filter patients based off their pan number
 3) Save one .xlxs per patient with filtered results
 4) Save filtered results in a run folder, with a logfile
 5) Move the unfiltered run file into the processed directory 

Errors will flag when:
- The xls has a different number of rows than expected

# "Double click to run filtering script.bat"

This is a windows batch file which allows the script to be run by users double clicking the logo.
</br>
A shortcut to the batch file has been made to prevent accidental deletion

# These scripts were developed by Viapath Genome Informatics
