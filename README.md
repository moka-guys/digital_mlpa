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
 2) Looks in Moka to find the gene symbols which match the pan number
 3) Filter patients based off their pan number
 4) Create a directory for the filtered files
 5) Save one .xlxs per patient with filtered results
 6) Save filtered results in the directory, with a logfile
 7) Flag samples which the pan number wasn't in Moka & which samples failed QC
 8) Move the unfiltered run file into the processed directory 

Errors will flag when:
- The xls has a different number of rows than expected
- There's an issue with the Moka connection


# "Double click to run filtering script.bat"

This is a windows batch file which allows the script to be run by users double clicking the logo.
</br>
A shortcut to the batch file has been made to prevent accidental deletion

# These scripts were developed by Viapath Genome Informatics
