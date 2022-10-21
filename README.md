# digital_mlpa
Scripts for supporting the digital MLPA service.
</br>
</br>
The output from the digital MLPA software provides results for all the probe regions covered.
</br>
To prevent incidental findings, these scripts have been created to filter the results based on a pan number per patient

Additional information can be found in the KB article (digital MLPA runs: KB0010393)

# digital_mlpa_filtering.py 

This script:
 - Imports unfiltered digital MLPA data from an xlsx
 - Checks there's the expected number of rows in the sheet
 - Checks if the sheet has been processed before. Denoted by the file name having "processed" in it
 - Checks the pan number for the patient is associated with the dMLPA category in Moka
 - Looks in Moka to find the gene symbols which match the pan number
 - Filter patients based off their pan number
 - Save one .xlxs per patient with filtered results
 - Create a directory for the filtered file, using the spreadsheet name as the title 
 - Save filtered results in the directory, with a logfile-
 - Flag samples in the logile where:
        - The pan number wasn't in Moka
        - The pan number was in Moka, but not in the dMLPA category 
        - Failed QC (and were therefore not processed)
 - Moves the unfiltered run file into the processed directory, and adds "_processed" on to it's file name

Errors will flag when:
- The xls has a different number of rows than expected
- There's an issue with the Moka connection


# "Double click to run filtering script.bat"

This is a windows batch file which allows the script to be run by users double clicking the logo.
</br>
A shortcut to the batch file has been made to prevent accidental deletion

# These scripts were developed by Viapath Genome Informatics
