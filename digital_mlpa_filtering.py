from lib2to3.pgen2.pgen import DFAState
from operator import index

from numpy import NaN
import digital_mlpa_filtering_config as config
import pandas as pd
import os
#import argparse 

# pip install xlsxwriter

### This script will ##
# 1) Import data from csv
# 2) Filter patients based off their pan number
# 3) Save one .xlxs per patient with filtered results
# 4) Move the unfiltered run file into a directory 



## ============ TO DO LIST ============================
# get this working on trust
#  Include debugging options - to do
# Include try and except statements - got some, could have more!
# Do a shape check for the number of rows?


''' ==================== SCRIPT FUNCTIONS ==================== '''

def load_file(run_file):
    # Load file
    df = pd.read_excel(config.path+run_file, header =1)
    # This second df is used to save later
    df_header_kept = pd.read_excel(config.path+run_file)
    #print(df_header_kept)
    #print("=================" + run_file + "================") 
    # Check if the files already been processed
    # will have processed in the file name
    if "processed" in run_file:
        print("Processed")
        processed_file = 1  
    else: 
        print ("To be processed")
        processed_file = 0      
    return(df, processed_file, df_header_kept)


def check_shape(df, processed_file):
   if processed_file == 0:
       row_count = len(df)
       if row_count != config.expected_rows:
           print("Spreadsheet has an unexpected number of rows!")
       else:
           print(" Correct shape, continuing")



def filter_df_and_save(run_df):
    # Empty df to add information to
    results_df = pd.DataFrame(columns = ["patient_id" , "pan_number", "genes_in_panel"]) 
    # Separate out the probes into one df & patients into another 
    #print(run_df)
    probes_df = run_df[['Probe order', 'Probe number', 'Gene', 'Exon', 'Mapview (hg38)', 'Chromosomal band (hg38)', 
            'Normal copy number', 'Probe type', 'Reference probe', 'Additional information', 'Unnamed: 12']]
    # Remove rows wwhere all the values are NaN
    probes_df=probes_df.dropna(how='all')
    # Make a patients only df 
    # Get all the patients whose results failed test
    # test the shape of this df and we don't want to save if there's nothing there?
    # Drop all the results which failed QC, put failed ones into a separate  <- * CHECK THIS IS WHAT JULIA WANTS *
    patient_results_df_failed = run_df[run_df.columns[run_df.iloc[6] == 'Failed']]
    # Save this somehow ## ============== TO DO
    # Make it based on a value which will be present only in the patient header 
    # or make it just be an exclusion of all the other columnns?
    # perhaps make the search function part of the config file <- * TO DO *
    # so it can be changed if the headers are ever changes
    patient_results_df = run_df.loc[:, run_df.columns.str.contains("Dig") ] 
    patient_results_passed_df = patient_results_df[patient_results_df.columns[patient_results_df.iloc[6] == 'Passed']]
    # Loop through each patient in the df
    for column in patient_results_passed_df:
        #print(column)
        # At the start of the loop, get the pan number from the header 
        # assign to variable
        patient_pan_number =column.split("-")[1]
        #print(patient_pan_number)
        try: 
            # Concat each colum from the patient results data frame on to the probe df
            per_patient_df = pd.concat([probes_df ,patient_results_passed_df[column]], axis = 1)
            #print(per_patient_df)
            # Filter the rows of the df, based on the value in genes, based on the patients pan number
            patient_gene_filtered_df = per_patient_df.loc[per_patient_df['Gene'].isin(config.gene_list[patient_pan_number])]
            # Get the sample info for each patient 
            sample_info = per_patient_df.iloc[0:6, 10:12]
            # save everything on one sheet #
            # Save both bits on different sheets #
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            # Can set widths, to filtering some columns out <- * after chat to Julia * TO DO *
            writer = pd.ExcelWriter(column + "_multiple.xlsx", engine="xlsxwriter")
            # Write each dataframe to a different worksheet.
            sample_info.to_excel(writer, sheet_name='Sample_info', index= False)
            patient_gene_filtered_df.to_excel(writer, sheet_name='Gene_filtered', index= False)
            # Close the Pandas Excel writer and output the Excel file.
            writer.save()
            success_string =("Patient from result " + column + " using pan number " 
                    + patient_pan_number + " saved. These genes " + 
                    (" ".join(config.gene_list[patient_pan_number])) + 
                    " have been used for filtering ")
            print(success_string)
            results_df= results_df.append({'patient_id': column ,  
                                'pan_number' : patient_pan_number,
                                'genes_in_panel': (" ".join(config.gene_list[patient_pan_number]))},
                                ignore_index=True)  
                #print(results_df)
        except: 
            # If pan number isn't present in config flag
            # Add to log
            results_df= results_df.append({'patient_id': column ,  
                                'pan_number' : patient_pan_number,
                                'genes_in_panel': "ERROR: Pan number not found in config"},
                                ignore_index=True)  
            print(patient_pan_number + " not found in config. Sample  " + column + 
                " could not be processed. Contact Binfx team to add to config : )" )
    return(results_df, patient_results_df_failed)



def create_and_save_logfile(logfile, failed_df, file_location_now, file):
    # Save the log file for each sample 
    # Check if any samples failed and add them to the log
    if failed_df.empty:
        print("No samples failed!")
        logfile= logfile.append({'patient_id': "No failed samples in run" ,  
                                'pan_number' : NaN ,
                                'genes_in_panel': NaN} ,
                                ignore_index=True) 
        #print(logfile)
    else:
        print("Samples did fail...")
        for column in failed_df:
            logfile= logfile.append({'patient_id': column ,  
                                    'pan_number' : "Sample failed" ,
                                    'genes_in_panel': "No filtering undertaken"} ,
                                    ignore_index=True) 
            #print(failed_df)
        #print(logfile)
    # Save the log file
    filepath = config.path+file.split(".")[0] + "_log.csv"
    logfile.to_csv(filepath, index= False)


def move_rename_processed_file(error_occurred, file_location, file):           
    # If no errors, move file to /processed directory
    try:
        if error_occurred  == False: 
            # Move the processed file, changing it's name 
            os.rename((file_location), (config.processed_path+file.split(".")[0] + "_processed.xls"))
            print("File moved & renamed")
        else:
            print("error occurred, not moving file")
    except:
        print('Could not move file to /processed folder. Is there a file with the same name in that folder?') 


'''================== Run script =========================== ''' 
count =0
for file in os.listdir(config.path):
    # Look for all .xlsx files in the folder  
    # Set this variable to false!
    files_to_process = False
    if file.endswith(".xls"):
        count = count +1
        # Attempt to load the file, check if it's already been processed 
        files_to_process = True
        loaded_df, processed_status, processed_df_to_save = load_file(file)
        file_location_now = config.path+file
        #to_move_location = config.processed_path+file
        if processed_status == 1:
            error_occurred  = False
            print("File has already been processed!")
        else:
            # File hasn't been processed, continue with processing 
            print("This file needs prcoessing, continue")
            # filter and save new files
            logfile, failed_samples = filter_df_and_save(loaded_df)
            # Mark them as processed 
            create_and_save_logfile(logfile, failed_samples, file_location_now, file)
            #error_occurred = False
            #mark_processed_file(error_occurred, processed_df_to_save, file_location_now)
            error_occurred  = False
            move_rename_processed_file(error_occurred, file_location_now, file )
            print("File moved")
    # Print out somewhere      
if count == 0:
    print( "No files ending in .xls in folder to process")
       





















