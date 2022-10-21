# coding: utf-8
# Paths
path = "P:/Bioinformatics/UAT/Julia_digital_MLPA_testing/"
#path = "H:/06_digital_mlpa/"
processed_path=path+"processed/"
logfile_path = path+"logfiles"

samplesheet_extension = ".xlsx"

# Expected features to check layout is the same
expected_row_count = 599

probe_headers = ['Probe order', 'Probe number', 'Gene', 'Exon', 'Mapview (hg38) in kb', 
                        'Chromosomal band (hg38)', 'Normal copy number', 'Probe type', 
                        'Reference probe', 'Additional information']

# Sample metrics values from column M of the spreadsheet
sample_info_names = ["Median total reads", "Sample type", "Estimated DNA quantity", "SNP code",
                                "Mutation probes detected" , "Reference probe quality", "Quality checks"]
