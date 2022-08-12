from numpy import NaN
import digital_mlpa_filtering_config as config
import pandas as pd
import os


### This script will ##
# 1) Import data from csv
# 2) Filter patients based off their pan number
# 3) Save one .xlxs per patient with filtered results
# 4) Save filtered results in a run folder, with a logfile
# 5) Move the unfiltered run file into a directory 

## ============ TO DO LIST ============================
#  Include debugging options - to do



''' ==================== SCRIPT FUNCTIONS ==================== '''


def load_file(file):
    # check if the file has already been processed
    if "processed" in file:
        file_processed = 1  
        error_occurred = False
        df = "empty_df"
    else: 
        # Load file
        df = pd.read_excel(config.path+file, header =1).reset_index(drop=True)
        # Check if the file has already been processed
        file_processed = 0
        if len(df.index) == config.expected_row_count:
            error_occurred = False
        else:
            error_occurred = True
    return(df, file_processed, error_occurred)


def make_run_folder(path_to_runfolder):
    # Make a run folder for the filtered samples  
    try: 
        os.makedirs(path_to_runfolder + "/logfile")
    except:
        file = path_to_runfolder.split("/")[2] 
        print("Can't make runfolder, does " + file + " already have a folder?")


def filter_df_and_save(run_df, path_to_runfolder):
    # Empty df to add information to later
    filters_used_df = pd.DataFrame(columns = ["Patient ID" , "Pan number", "Genes in panel"]) 
    # Separate out the probes into one df & patients into another 
    probes_df = run_df[['Probe order', 'Probe number', 'Gene', 'Exon', 'Mapview (hg38)', 
                        'Chromosomal band (hg38)', 'Normal copy number', 'Probe type', 
                        'Reference probe', 'Additional information']]
    # Remove NaN rows 
    probes_df=probes_df.dropna(how='all')
    # Put QC failed samples into a separate df  <- * CHECK THIS IS WHAT JULIA WANTS *
    patient_results_failed_df = run_df[run_df.columns[run_df.iloc[6] == 'Failed']]
    # Get all the samples which passed QC
    patient_results_passed_df = run_df[run_df.columns[run_df.iloc[6] == 'Passed']]
    # Loop through each column (patient result) in the df
    for column in patient_results_passed_df:
        # At the start of the loop, get the pan number from the header 
        patient_pan_number =column.split("-")[1]
        try: 
            # Get the sample info for each patient 
            sample_info = patient_results_passed_df[column].drop(patient_results_passed_df[column].index[7:])
            # turn it into a dataframe for saving later
            sample_info = sample_info.to_frame()
            # Attach the row headers from the config
            sample_info.insert(0, "sample_info_pt", config.sample_info_names)
            # Make a data frame which is only the results of the patient being looped over
            patient_results_passed_drop_df = patient_results_passed_df[column].drop(patient_results_passed_df[column].index[0:7])
            # Concat the probes dataframe to the patients results
            per_patient_df = pd.concat([probes_df ,patient_results_passed_drop_df], axis = 1)
            # Filter the rows of the df, based on the value in genes, based on the patients pan number
            patient_gene_filtered_df = per_patient_df.loc[per_patient_df['Gene'].isin(config.gene_list[patient_pan_number])]
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            # Can set widths, to filtering some columns out <- * after chat to Julia * TO DO *
            writer = pd.ExcelWriter(path_to_runfolder + "/" + column + "_filtered_results.xlsx", engine="xlsxwriter")
            # Write each dataframe to a different worksheet.
            sample_info.to_excel(writer, sheet_name='Sample info', index= False)
            patient_gene_filtered_df.to_excel(writer, sheet_name='Gene filtered results', index= False)
            # Close the Pandas Excel writer and output the Excel file.
            writer.save()
            # Append the patient ID and genes used in filtering to the log file 
            filters_used_df= filters_used_df.append({'Patient ID': column ,  
                                'Pan number' : patient_pan_number,
                                'Genes in panel': (" ".join(config.gene_list[patient_pan_number]))},
                                ignore_index=True)  
        except: 
            # If pan number isn't present in config add to log
            filters_used_df= filters_used_df.append({'Patient ID': column ,  
                                'Pan number' : patient_pan_number,
                                'Genes in panel': "ERROR: Pan number not found in config"},
                                ignore_index=True)  
    return(filters_used_df, patient_results_failed_df)
 

def create_and_save_logfile(logfile, failed_df,  path_to_runfolder):
    # Save the log file for each sample 
    # Check if any samples failed and add them to the log
    if failed_df.empty:
        logfile= logfile.append({'Patient ID': "No failed samples in run" ,  
                                'Pan number' : NaN ,
                                'Genes in panel': NaN} ,
                                ignore_index=True) 
    else:
        #print("Please check log for this run")
        for column in failed_df:
            logfile= logfile.append({'Patient ID': column ,  
                                    'Pan number' : "Sample failed" ,
                                    'Genes in panel': "No filtering undertaken"} ,
                                    ignore_index=True)    
    filepath_log = path_to_runfolder +"/logfile/"+file.split(".")[0] + "_log.csv"
    logfile.to_csv(filepath_log, index= False)


               
def move_rename_processed_file(error_occurred, file):           
    # If no errors, rename & move file to /processed directory
    try:
            # Change the file name
            os.rename((config.path+file), 
                        (config.path+file.split(".")[0] + "_processed.xls"))
            # Then move it 
            os.rename((config.path+file.split(".")[0] + "_processed.xls"), 
                        (config.processed_path+file.split(".")[0] + "_processed.xls"))
            print("Proccessed file renamed and moved to /processed folder")
    except:
        print('Could not move file to /processed folder. Is there a file with the same name in that folder?') 


'''================== Run script =========================== ''' 

# Counter for if there are no sheets to process
count =0
try:
    for file in os.listdir(config.path):
        # Look for all .xlsx files in the folder 
        if file.endswith(".xls"):
            print("Found this .xls file : " + file)
            count = count +1
            # Load the file & check if it's already been processed  
            loaded_df, processed_status, error_occurred = load_file(file)
            # File doesn't have the expected number of rows
            if error_occurred == True:
                with open(config.path + "error_log_"+ file.split(".")[0] + ".txt", "w") as f:
                        f.write ("Results sheet doesn't have the expected number of rows. Contact bioinformatics team")
                        print("ERROR OCCURRED, please see error_log file")     
            if processed_status == 1:
                print(file + " has already been processed")
            elif error_occurred == False:
                # File hasn't been processed, continue with processing 
                print(file + " has not been processed, running filtering scripts")
                # Create path to runfolder
                path_to_runfolder = config.path+file.split(".")[0]
                # Make run folder directory 
                make_run_folder(path_to_runfolder)
                # Filter and save new files
                logfile, failed_samples = filter_df_and_save(loaded_df, path_to_runfolder)
                # Create logfile per run
                create_and_save_logfile(logfile, failed_samples,  path_to_runfolder)
                # Mark them as processed 
                move_rename_processed_file(error_occurred, file)
    if count == 0:
        print( "No files ending in .xls in folder to process")
except:
    print("Unexpected error occurred, contain bioinformatics team")       





















