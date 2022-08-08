import digital_mlpa_filtering_config as config
import pandas as pd
import os

# pip install xlsxwriter

# 1) Import data from csv
# challenge will be data sometimes moves... 
# 2) filter patients based off their pan number
# do this using a function, with row and filtering needed as an input
# 3) save one csv per patient with filtered results
# 4) move the old unfiltered file into a directory 
# 5) Include debugging options 
# 6) Include try and except statements 
# 7) Include a check when opening to see if it's been filtered or not, somehow...

## ============ TO DO LIST ============================
## Move processed file to another folder  - done 
## Enable script to be run from a button click of an icon 
## Error handling when pan number isn't found in config - done 
## Error handling if spreadsheet is in wrong format 
## Way to check if file has been processed or not? 
# Add steps and processes to a df, per sample and save to a log
# rename if processed or add additional sheet in to unfiltered sheet 


''' ==================== SCRIPT FUNCTIONS ==================== '''


def load_file(run_file):
    # Load file
    df = pd.read_excel(config.path+run_file, header =1)
    print("=================" + run_file + "================")
    # Check if the files already been processed
    if "Processed" in df.columns:
        print("Processed")
        processed_file = 1
        # Attempt to move this file to the processed directory
        move_processed_file(error_occurred, file_location_now, to_move_location)   
    else: 
        print ("To be processed")
        processed_file = 0
        #print(list(df.columns))
    return(df, processed_file)


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
    # Make another df from the patient_results_passed_df which contains the sample information (but not the probe values)
    # Select rows 0-7 for new df
    patient_sample_info_df = patient_results_passed_df.iloc[0:7]
    # At the start of the loop, get the pan number from the header 
    # assign to variable 
    for column in patient_sample_info_df:
        #print(column)
        # Get each patients pan number by splitting the column header
        # Something to check if the pan number isn't present here in log
        # return the pan number used that isn't present into the log with the patient ID?
        patient_pan_number =column.split("-")[1]
        #print(patient_pan_number)
        try: 
            # Concat each colum from the patient results data frame on to the probe df
            per_patient_df = pd.concat([probes_df ,patient_sample_info_df[column]], axis = 1)
            # Filter the rows of the df, based on the value in genes, based on the patients pan number
            # also keep them if the value in unamed: 12 is not NaN
            patient_gene_filtered_df = per_patient_df.loc[per_patient_df['Gene'].isin(config.gene_list[patient_pan_number])]
            #filtered_df = per_patient_df.loc[per_patient_df['Unamed: 12'].notnull()]
            sample_info = per_patient_df[per_patient_df['Unnamed: 12'].notnull()]
            # save everything on one sheet #
            # Save both bits on different sheets #
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            # Can set widths, to filtering some columns out <- * after chat to Julia * TO DO *
            writer = pd.ExcelWriter(column + "_multiple.xlsx", engine="xlsxwriter")
            # Write each dataframe to a different worksheet.
            sample_info.to_excel(writer, sheet_name='Sample_info')
            patient_gene_filtered_df.to_excel(writer, sheet_name='Gene_filtered')
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
    return(results_df)

#def mark_processed_file(file):



def move_processed_file(error_occurred, file_location, processed_folder):           
    # If no errors, move file to /Booked directory
    try:
        if error_occurred  != True: 
            # Move the processed file
            os.rename((file_location), (processed_folder))
            print("File moved")
        else:
            print("error occurred, not moving file")
    except:
        print('Could not move file to /processed folder. Is there a file with the same name in that folder?') 


'''================== Run script =========================== ''' 

for file in os.listdir(config.path):
    # Look for all .txt files in the folder  
    if file.endswith(".xls"):
        # Attempt to load the file, check if it's already been processed 
        files_to_process = True
        loaded_df, processed_status = load_file(file)
        file_location_now = config.path+file
        to_move_location = config.processed_path+file
        if processed_status == 1:
            error_occurred  = False
            
            print(" this file hasn't been processed, but it has been moved!")
        else:
            # File hasn't been processed, continue with processing 
            print("This file needs prcoessing, continue")
            filter_df_and_save(loaded_df)
            error_occurred  = False
            #move_processed_file(error_occurred, file_location_now, to_move_location )
            print("File moved")
        if files_to_process == False:
            print( "No files ending in .xls in folder to process")




        




















# Make one df per patient 
# for column in patient_results_passed_data_df:
# # each column in the data frame 
# # Append the probe data frame 

#     print(column)
#     columnSeriesObj = patient_results_passed_data_df[column]
#     print('Column Name : ', column)
#     print('Column Contents : ', columnSeriesObj.values)




