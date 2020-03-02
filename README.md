# app-data

## Preprocessing
#### Combine records belonging to each user together
#### For each user, sort records by time and remove duplicated records
## Processing
#### The codes are to extract trip ends from app-based data. They are integrated by the main file, main.py. Instructions for deploying environment for running the codes correctly are specified in main.py
#### In the main function, there are four blocks: read in data; extract gps stays; extract cellular stays; integrate gps stays and cellular stays.  The logic of the workflow can be found in the recent published paper: https://arxiv.org/abs/1912.01835
#### For each block of codes, comments are embeded in the codes to help understanding. 
#### A data desciption of the input data can be found in file Analytics_MX_spec_by_Cuebiq.pdf as well as comments in the codes. 
#### A data desciption of the output data can be found in file data_dictionary_for_trip_identified_by_Feilong.pdf
#### Additional notes can be found in file Dictionaries_of_Cuebiq_data_and_notes_of_data_processing_by_Feilong.pdf
## Postprocessing
#### Codes that would be helpful to leverage the processed data for some analysis
