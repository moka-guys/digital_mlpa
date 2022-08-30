#python 3.10.10
from numpy import NaN
import pandas as pd
import os
from configparser import ConfigParser
from datetime import date
import pyodbc 
import xlrd
import xlsxwriter
import sys

# Need to change the python path to find the config
path_to_config = "H:/06_digital_mlpa/scripts"
sys.path.insert(0, path_to_config)
import digital_mlpa_filtering_config as config


### This script will ##
# 1) Import data from csv
# 2) Send a query to Moka for the genes based on the pan numbers
# 3) Filter patients based off their pan number
# 4) Save one .xlxs per patient with filtered results
# 5) Save filtered results in a run folder, with a logfile
# 6) Move the unfiltered run file into a directory 


''' =================== MOKA CONNECTIONS ==================== '''

# Read config file(must be called config.ini and stored in the same directory as script)
config_parser = ConfigParser()
print_config = config_parser.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini"))

class MokaConnector(object):
    """
    pyodbc connection to Moka database for use by other functions
    
    """
    def __init__(self):
        self.cnxn = pyodbc.connect('DRIVER={{SQL Server}}; SERVER={server}; DATABASE={database};'.format(
            server=config_parser.get("MOKA", "SERVER"),
            database=config_parser.get("MOKA", "DATABASE")
            ),
            autocommit=True
        )
        self.cursor = self.cnxn.cursor()

    def __del__(self):
        """
        Close connection when object destroyed
        """
        self.cnxn.close()

    def execute(self, sql):
        """
        Execute SQL, without catching return values (INSERT, UPDATE etc.)
        """
        self.cursor.execute(sql)

    def fetchall(self, sql):
        """
        Execute SQL catching all return records (SELECT etc.)
        """
        return self.cursor.execute(sql).fetchall()

    def fetchone(self, sql):
        """
        Execute SQL catching one returned record (SELECT etc.)
        """
        return self.cursor.execute(sql).fetchone()


''' ==================== SCRIPT FUNCTIONS ==================== '''


def load_file(file):
    '''
    This function checks if files have already been processed 
    Loads it into a dataframe and checks it has the expected number of rows
    INPUT: Path to a .xlsx file
    RETURN: dataframe, boolean of processed status, boolean for error
    '''
    if "processed" in file:
        file_processed = 1  
        error_occurred = False
        df = "empty_df"
    else: 
        # Load file
        df = pd.read_excel(config.path+file, header =4).reset_index(drop=True)
        file_processed = 0
        # Check df has expected row count
        if len(df.index) == config.expected_row_count:
            error_occurred = False
        else:
            error_occurred = True
    return(df, file_processed, error_occurred)

def error_log(path, error_message):
    '''
    This function creates & writes to an error log
    INPUT: path, error message
    RETURN: None
    '''
    date = today.strftime("%b-%d-%Y")
    error_message = str(error_message)
    with open(config.path + "error_log_"+ date + ".txt", "w") as f:
            f.write (error_message)
            print("ERROR OCCURRED, please see error_log file")



def make_run_folder(path_to_runfolder, file):
    '''
    This function creates the run folder for the filtered results to go into
    INPUT: Path to run sheet being processed 
    RETURN: None
    '''
    try: 
        os.makedirs(path_to_runfolder + "/logfile")
    except:
        #file = path_to_runfolder.split("/")[2] 
        print("Can't make runfolder, does " + file + " already have a folder?")


def get_gene_symbols_from_moka(run_df):
    '''
    This queries moka to find the gene symbols list 
    for each pan number in the spreadsheet
    INPUT: Path to run sheet being processed 
    RETURN: Pan numbers with genes
    '''
    try:
        exception_error_msg = None
        pan_numbers_to_find_in_moka = []
        pan_numbers_with_genes = {}
        # Get all the patients who passed QC
        patient_results_passed_df = run_df[run_df.columns[run_df.iloc[6] == 'Passed']]
        # Get just the sample names 
        df_headers = patient_results_passed_df.columns.values.tolist()
        for sample_name in df_headers:
            # Get the Pan number
            pan_number = sample_name.split("_")[2]
            pan_numbers_to_find_in_moka.append(pan_number)
        # Get all the unique pan numbers in the df
        unique_pan_numbers_to_find = list(set(pan_numbers_to_find_in_moka))
        # For each unique pan number, query Moka for the gene symbols 
        for patient_pan_number in unique_pan_numbers_to_find:
            # Query moks to check the pan number is in the dMLPA category 
            check_dmlpa = ( " SELECT [NGSPanel].[Category] "
                        " FROM [NGSPanel]  "
                        " WHERE [NGSPanel].[PanelCode]='{pan_number}'"
            ).format(
                pan_number = patient_pan_number 
            )
            # Execute SQL query
            check_dmlpa_sql = mc.fetchall(check_dmlpa)
            # Make the list of tuples into a list
            check_dmlpa_list = ['","'.join(map(str, row)) for row in check_dmlpa_sql]
            #print(check_dmlpa_list)
            # If the list is empty, that denotes the pan number isn't in Moka
            if not check_dmlpa_list:
                gene_list = 1
                pan_numbers_with_genes[patient_pan_number] = gene_list
            # dMLPA category ID is 5138
            # Check if the first element of the list matches
                # Everythin went ok, error message is blank
               # exception_error_msg = "blank"
            elif '5138' not in check_dmlpa_list[0]:
                gene_list = 2
                pan_numbers_with_genes[patient_pan_number] = gene_list
                # Everythin went ok, error message is blank
                #exception_error_msg = "blank"
            else:
                # This pan number is in the dMLPA category
                # Build SQL query
                get_genes = ( " SELECT [NGSPanelGenes].[Symbol] "
                        " FROM [NGSPanelGenes] INNER JOIN [NGSPanel] ON [NGSPanelGenes].[NGSPanelID] = [NGSPanel].[NGSPanelID] "
                        " WHERE [NGSPanel].[PanelCode]='{pan_number}'"
                    ).format(
                        pan_number = patient_pan_number 
                    )
                # Execute SQL query
                get_genes_sql = mc.fetchall(get_genes) 
                # Above query returns a list of tuples, this makes it into a list
                gene_list = ['","'.join(map(str, row)) for row in get_genes_sql]
                # Add the gene lists to a dictionary, where the pan number 
                # is the key and the list of genes in the value pair 
                pan_numbers_with_genes[patient_pan_number] = gene_list
    except Exception as exception_error_msg:
        print("Error occured, check log")
    return(pan_numbers_with_genes, exception_error_msg)
    

def filter_results(run_df, path_to_runfolder, pan_numbers_genes_dic):
    '''
    This function splits the spreadsheet into different dataframes
    Probe names, control probes and patient results 
    Patient results are filtered by gene list & then added to other dfs
    Saves a per patient sheet 
    Populates a log of which samples were filtered with which genes
    INPUT: df for spreadsheet being processed, path to run sheet being processed 
    RETURN: Filters used on each sample for logging, a df of any samples which failed QC
    '''
    # Empty df to add information to later
    filters_used_df = pd.DataFrame(columns = ["Patient ID" , "Pan number", "Genes in panel"]) 
    # Make a df of just the probes information 
    probes_df = run_df[config.probe_headers]
    # Remove NaN rows 
    probes_df=probes_df.dropna(how='all')
    # Put QC failed samples into a separate df 
    patient_results_failed_df = run_df[run_df.columns[run_df.iloc[6] == 'Failed']]
    # Get all the patients who passed QC
    patient_results_passed_df = run_df[run_df.columns[run_df.iloc[6] == 'Passed']]
    # Get all the unique headers in the df
    # For each unique pan number, query Moka for the gene symbols 
    for column in patient_results_passed_df:
        patient_pan_number =column.split("_")[2]
        try:
            exception_error_msg = None
            # Get the sample info for each patient 
            sample_info = patient_results_passed_df[column].drop(patient_results_passed_df[column].index[7:])
            # turn it into a dataframe for saving later
            sample_info = sample_info.to_frame()
            # Attach the row headers from the config
            sample_info.insert(0, "sample_info_pt", config.sample_info_names)
            # Make a data frame which is only the probe results of the patient being looped over
            patient_results_passed_drop_df = patient_results_passed_df[column].drop(patient_results_passed_df[column].index[0:7])
            # Concat the probes dataframe to the patients results
            per_patient_df = pd.concat([probes_df ,patient_results_passed_drop_df], axis = 1)
            # Build genes used in filtering log 
            if pan_numbers_genes_dic[patient_pan_number] == 1:
                # If the pan number wasn't in Moka
                filters_used_df_patient = pd.DataFrame({'Patient ID': column ,  
                                    'Pan number' : patient_pan_number,
                                    'Genes in panel': "ERROR: Pan number not found in Moka"},
                                    index = [0,1,2])  
                filters_used_df = pd.concat([filters_used_df,filters_used_df_patient], axis = 0, ignore_index = True)
            elif pan_numbers_genes_dic[patient_pan_number] == 2:
                # If the pan number is in Moka, but doesn't have the dMLPA category
                filters_used_df_patient = pd.DataFrame({'Patient ID': column ,  
                                    'Pan number' : patient_pan_number,
                                    'Genes in panel': "ERROR: Pan number in Moka but not in dMLPA category"},
                                    index = [0,1,2])  
                filters_used_df = pd.concat([filters_used_df,filters_used_df_patient], axis = 0, ignore_index = True)
            else:
                # Does have an dMLPA pan number in Moka
                # Filter the rows of the df, based on the value in genes, based on the patients pan number
                patient_gene_filtered_df = per_patient_df.loc[per_patient_df['Gene'].isin(pan_numbers_genes_dic[patient_pan_number])]  
                # Get the control probes for this patient
                patient_control_df = per_patient_df.loc[per_patient_df['Probe type'].str.match("CTRL")]
                # Concat the gene filtered & control probes
                patient_gene_filtered_control_df = pd.concat([patient_gene_filtered_df, patient_control_df])
                # Convert the results column to a float
                # Will raise a message to user about changes being on a copy, errors flag stops this
                # Round to three significant figures 
                patient_gene_filtered_control_df[column] =patient_gene_filtered_control_df[column].astype(float, errors ="ignore").round(3)
                # Create a xlsx to write data too
                writer = pd.ExcelWriter(path_to_runfolder + "/" + column + "_filtered_results.xlsx", engine="xlsxwriter")
                # Write each dataframe to a different worksheet.
                sample_info.to_excel(writer, sheet_name='Sample info', index= False)
                patient_gene_filtered_control_df.to_excel(writer, sheet_name='Gene filtered results', index= False)
                # Close the Pandas Excel writer and output the Excel file.
                writer.save()
                #  Make a df of the genes used for this sample
                filters_used_df_patient= pd.DataFrame({'Patient ID': column ,  
                                    'Pan number' : patient_pan_number,
                                    'Genes in panel': [(" ".join((pan_numbers_genes_dic[patient_pan_number])))]}
                                    , index = [0,1,2])   

                filters_used_df = pd.concat([filters_used_df,filters_used_df_patient], axis = 0, ignore_index = True)
        except Exception as exception_error_msg:
            print("Error occured, check log")        
    return(filters_used_df, patient_results_failed_df, exception_error_msg)
      
 

def create_and_save_logfile(logfile, failed_df,  path_to_runfolder):
    '''
    This function saves a log file based on the filtering 
    for each samples
    INPUT: Logfile df, failed samples df, path to runfolder
    RETURN: None
    '''
    # Save the log file for each sample 
    # Check if any samples failed and add them to the log
    if failed_df.empty:
        # Make a df of failed sample information 
        # Add it to the bottom of the log 
        logfile_no_failed_samples =  pd.DataFrame({'Patient ID': "No failed samples in run" ,  
                                'Pan number' : NaN ,
                                'Genes in panel': NaN} ,
                                  index = [0,1,2]) 
        logfile = pd.concat([logfile, logfile_no_failed_samples], axis = 0, ignore_index = True)
    else:
        for column in failed_df:
            logfile_failed_samples  = pd.DataFrame({'Patient ID': column ,  
                                    'Pan number' : "Sample failed" ,
                                    'Genes in panel': "No filtering undertaken"} ,
                                      index = [0,1,2])    
            logfile = pd.concat([logfile, logfile_failed_samples], axis = 0, ignore_index = True)
    # As this df was made in a loop, there are duplicate entries 
    logfile_duplicates_removed = logfile.drop_duplicates()
    filepath_log = path_to_runfolder +"/logfile/"+file.split(".")[0] + "_log.csv"
    logfile_duplicates_removed.to_csv(filepath_log, index= False)


               
def move_rename_processed_file(error_occurred, file):     
    '''
    This function saves a log file based on the filtering 
    for each samples
    INPUT: Logfile df, failed samples df, path to runfolder
    RETURN: None
    '''      
    # If no errors, rename & move file to /processed directory
    try:
            # Change the file name
            os.rename((config.path+file), 
                        (config.path+file.split(".")[0] + "_processed" + config.samplesheet_extension))
            # Then move it 
            os.rename((config.path+file.split(".")[0] + "_processed" + config.samplesheet_extension), 
                        (config.processed_path+file.split(".")[0] + "_processed" + config.samplesheet_extension))
            print("Proccessed file renamed and moved to /processed folder")
    except:
        print('Could not move file to /processed folder. Is there a file with the same name in that folder?') 



'''================== One off variables =========================== '''

today = date.today()
# Attempt to instantiate moka connector
try:
    mc = MokaConnector()
except Exception as exception_error_msg:
    print("Error connecting to Moka")
    error_message = str(exception_error_msg) + ". Error connecting to Moka. Contact bioinformatics team "
    path_to_runfolder = config.path
    error_log(path_to_runfolder, error_message)
    exit()
    
'''================== Run script =========================== ''' 

# Counter for if there are no sheets to process
count =0
try:
    for file in os.listdir(config.path):	
        # Look for all .xlsx files in the folder 
        if file.endswith(config.samplesheet_extension):
            print("Found this " + config.samplesheet_extension + " file : " + file)
            count = count +1
            # Load the file & check if it's already been processed  
            loaded_df, processed_status, error_occurred = load_file(file)
            # File doesn't have the expected number of rows
            # Create path to runfolder
            path_to_runfolder = config.path+file.split(".")[0]
            if error_occurred == True:
                error_message = file + " sheet doesn't have the expected number of rows. Contact bioinformatics team "
                error_log(path_to_runfolder, error_message)    
            if processed_status == 1:
                print(file + " has already been processed")
            elif error_occurred == False:
                # File hasn't been processed, continue with processing 
                print(file + " has not been processed, running filtering scripts")
                # Make run folder directory 
                make_run_folder(path_to_runfolder, file)
                # Filter and save new files via a moka query for genes
                gene_list, exception_error_msg = get_gene_symbols_from_moka(loaded_df)
                if exception_error_msg is not None:
                    error_log(path_to_runfolder,  exception_error_msg)
                else:
                    logfile, failed_samples, exception_error_msg = filter_results(loaded_df, path_to_runfolder, gene_list)
                    # Create logfile per run
                    create_and_save_logfile(logfile, failed_samples,  path_to_runfolder)
                    if exception_error_msg is not None:
                        error_log(path_to_runfolder,  exception_error_msg)
                    else:
                    # Mark them as processed 
                        move_rename_processed_file(error_occurred, file)
    if count == 0:
        print( "No files ending in " + config.samplesheet_extension + " in folder to process")
except Exception as exception_error_msg:
    error_occurred = True
    if error_occurred == True:
        # If an unknown error occurred, save to error file
        path_to_runfolder = config.path
        error_log(path_to_runfolder,  exception_error_msg)
        print("Unexpected error occurred, contain bioinformatics team")       
