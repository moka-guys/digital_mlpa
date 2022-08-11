#path="/home/erin/Documents/Work/digital_mlpa/digital_mlpa/"
# Paths
path = "H:/06_digital_mlpa/"
processed_path=path+"processed/"
logfile_path = path+"logfiles"

# Expected row count to do a sense check if spreadsheet layout has changes
expected_row_count = 594

# Sample metrics values from column M of the spreadsheet
sample_info_names = ["Median total reads", "Sample type", "Estimated DNA quantity", "SNP code",
                                "Mutation probes detected" , "Reference probe quality", "Quality checks"]

# Gene lists
gene_list = {"Pan49" : ["APC", "BMPR1A"],
             "Pan50" : ["MLH1", "MSH2"],
             "Pan51" : ["MLH1", "BMPR1A"], 
             "Pan52" : ["EPCAM", "MUTYH", "PMS2"],
             "Pan53" : ["PTEN", "CDKN2A", "ATM2"]  }
