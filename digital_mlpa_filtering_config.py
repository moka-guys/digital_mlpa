# coding: utf-8
# Paths
#path = "P:/Bioinformatics/UAT/Julia_digital_MLPA_testing/"
path = "home/natasha/Documents"
#path = "H:/06_digital_mlpa/"
processed_path=path+"processed/"
logfile_path = path+"logfiles"

# Expected features to check layout is the same
expected_row_count = 594

# Sample metrics values from column M of the spreadsheet
sample_info_names = ["Median total reads", "Sample type", "Estimated DNA quantity", "SNP code",
                                "Mutation probes detected" , "Reference probe quality", "Quality checks"]
