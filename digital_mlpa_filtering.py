import digital_mlpa_filtering_config as config
import pandas as pd

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


''' ==================== SCRIPT FUNCTIONS ==================== '''



'''================== Run script =========================== ''' 

# 1) Import data from csv
# challenge will be data sometimes moves... 

df_path=config.path+"DigMLPA3 - Ratios.xls"
print(df_path)
# Import csv but remove the top line as it's not needed
df = pd.read_excel(config.path+"DigMLPA 3 - Ratios_edited.xls", header=1)
#print(list(df.columns))


# 2) Separate out the probes into one df & patients into another 
probes_df = df[['Probe order', 'Probe number', 'Gene', 'Exon', 'Mapview (hg38)', 'Chromosomal band (hg38)', 
            'Normal copy number', 'Probe type', 'Reference probe', 'Additional information', 'Unnamed: 12']]
# Remove rows wwhere all the values are NaN
probes_df=probes_df.dropna(how='all')

#print(probes_df)
# Make a patients only df 
# Get all the patients whose results failed test
# test the shape of this df and we don't want to save if there's nothing there?
# Drop all the results which failed QC, put failed ones into a separate  <- * CHECK THIS IS WHAT JULIA WANTS *

patient_results_df_failed = df[df.columns[df.iloc[6] == 'Failed']]

# Make it based on a value which will be present only in the patient header 
# or make it just be an exclusion of all the other columnns?
# perhaps make the search function part of the config file <- * TO DO *
# so it can be changed if the headers are ever changes
patient_results_df = df.loc[:, df.columns.str.contains("Dig") ] 
patient_results_passed_df = patient_results_df[patient_results_df.columns[patient_results_df.iloc[6] == 'Passed']]

# Make another df from the patient_results_passed_df which contains the sample information (but not the probe values)
# Select rows 0-7 for new df
patient_sample_info_df = patient_results_passed_df.iloc[0:7]

# Drop the patient info rows from the main df 
#patient_results_passed_data_df = patient_results_passed_df.drop(patient_results_passed_df.index[0:7])
patient_results_passed_data_df = patient_results_passed_df


#patient_results_passed_data_df_one =patient_results_passed_data_df["BP01-pan49 - DigMLPA1"]

# At the start of the loop, get the pan number from the header 
# assign to variable 
for column in patient_results_passed_data_df:
    # Get each patients pan number by splitting the column header
    patient_pan_number =column.split("_")[1]
    # Concat each colum from the patient results data frame on to the probe df
    per_patient_df = pd.concat([probes_df ,patient_results_passed_data_df[column]], axis = 1)
    #print(per_patient_df)
    # Filter the rows of the df, based on the value in genes, based on the patients pan number
    # also keep them if the value in unamed: 12 is not NaN
    patient_gene_filtered_df = per_patient_df.loc[per_patient_df['Gene'].isin(config.gene_list[patient_pan_number])]
    #filtered_df = per_patient_df.loc[per_patient_df['Unamed: 12'].notnull()]
    sample_info = per_patient_df[per_patient_df['Unnamed: 12'].notnull()]
    # save everything on one sheet #
    #patient_df_to_save_one_sheet = pd.concat([sample_info, patient_gene_filtered_df], axis = 0)
    #patient_df_to_save_one_sheet.to_csv(column + "single.csv", index = False)
    # Save both bits on different sheets #
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    # Can set widths, to filtering some columns out <- * after chat to Julia * TO DO *
    writer = pd.ExcelWriter(column + "_multiple.xlsx", engine="xlsxwriter")
    #writer = pd.ExcelWriter('pandas_multiple.xlsx', engine='xlsxwriter')
    # Write each dataframe to a different worksheet.
    sample_info.to_excel(writer, sheet_name='Sample_info')
    patient_gene_filtered_df.to_excel(writer, sheet_name='Gene_filtered')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print("Patient from result " + column + " and ")















# Make one df per patient 
# for column in patient_results_passed_data_df:
# # each column in the data frame 
# # Append the probe data frame 

#     print(column)
#     columnSeriesObj = patient_results_passed_data_df[column]
#     print('Column Name : ', column)
#     print('Column Contents : ', columnSeriesObj.values)




