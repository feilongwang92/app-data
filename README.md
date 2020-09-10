### Documentation of GitHub app data repository
The codes are in three folders, including the preprocessing, processing, and postprocessing folders. 
- The codes in the preprocessing folder are to combine together records belonging to each user and contained many tiny files, sort records by time and remove duplicated records. 
- The codes in the processing folder are to extract trip ends from the data. The methodology based on which the codes are developed can be found in the recently published paper "[*Extracting trips from multi-sourced data for mobility pattern analysis: An app-based data example*](https://www.sciencedirect.com/science/article/pii/S0968090X18316085)". 
- The codes in the postprocessing folder serve examples of using the processing data for mobility pattern analyses.

In the following, codes in each folder are introduced in detail. Comments embedded in the codes are also helpful to understand the codes.

At the end of this document, instructions for deploying the computational environment are specified. Note that codes are in **Python 2.7**. The outcomes could be sensitive to the computational environment. 

The descriptions of the raw data and the processed data can be found in file "Dictionaries of Cuebiq data and notes of data processing". The data structure of storing the data in memory can be found in code comments. The workflow of processing the data is introduced in file "Workflow of data processing". You may find it helpful to understand the codes in the processing folder.

#### Codes in Preprocessing Folder: 
There are three python files in the preprocessing folder. To understand the purpose of each file, you first need to know how raw data are organized into folders and small files by Cuebiq.
##### Raw Data Folders:
Raw data are sorted into a series of gzipped files, partitioned into folders by date. The folder names will represent the day on which the data was processed by Cubiq. For example,
2018010100 - meaning the data was processed on January 1, 2018
2018010200 - meaning the data was processed on January 2, 2018
2018010300 - meaning the data was processed on January 3, 2018
According to emails from Cuebiq, data are processed at 12AM UTC and there can also be a certain lag in the data. Cuebiq receives the data as it is batched on a device before being sent to Cuebiq’s servers, therefore the timestamps in each dated folder may not represent only that day and could potentially include some data from additional dates.  The rule of thumb is that if each data folder will have 90+% of data for a given day looking at the data for that day and the following day. So, for example, 90+% of data for January 1, 2018 would be found in folders:
2018010100 - meaning the data was processed on January 1, 2018
2018010200 - meaning the data was processed on January 2, 2018

Figure 1 includes several snaps showing how data are organized in folders, as introduced above. Each day is a folder containing many smaller gzipped files. After each of the smaller gzipped files is unzipped, it becomes a csv file containing multiple users. The size of each csv file is similar. It is possible that a single user have the same, similar or different records showing in multiple files for the same day. Each record contains 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Time zone offset. The meaning of each column is provided in another document named “Dictionaries of Cuebiq data and notes of data processing by Feilong.doc”.


![](https://pandao.github.io/editor.md/examples/images/4.jg)

> Figure 1. Directory structure of the data before and after step 1. (a) organized by the data vendor, records of each day are within one folder but not in one file (figure shows 9 days); (b) in each folder, there are hundreds of small zipped, csv files, each containing thousands of records belonging to multiple users; (c) after step 1 (unzip and combine small files), records on one day are in one csv file (figure shows 9 days).

##### [step1_unzip_combine_file.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step1_unzip_combine_file.py "step1_unzip_combine_file.py")
Codes in this file is to process the zipped files originally provided, unzip them, and put them into another folder as a user-specified code. 
- Input files: raw zipped files provided by the vendor (zipped files as well). The input directory is also embedded in the python code. The structure of data files from the vendor is shown in figure 1 (a) and (b).
- Output files: for each day, there will be one csv file containing all the users for that day. For example, if the time period is 60 days, there will be 60 csv files generated. The output directory is embedded in the python code. The data structure of output files is shown in Figure 1 (c).

How to run it:  
`python step1_unzip_combine_file.py "E:/data"`  
Here, the string `"E:/data"` gives the directory of the raw folder. 

##### [step2_getAllUserId.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step2_getAllUserId.py "step2_getAllUserId.py") 
Extract user ids from the output files from the previous program. 
- Input files: 60 csv files outputted from the previous program
- Output: an output file containing all user ids.

How to run it:  
`python step2_getAllUserId.py "E:/data"`  
Here, the string `"E:/data"` gives the folder directory of the unzipped data. 

##### [step3_gatherTracesofEachUser_removeDuplicate.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step3_gatherTracesOfEachUser_RemoveDuplicate.py "step3_gatherTracesofEachUser_removeDuplicate.py") 

Take in the previous output files, for each user, append multiple files for the same user together, so that for a single user, all his/her records will be contained in a single file. Sort all records for each user by time and remove duplicates (if multiple records have the same time but different location information, you retain the record with lower uncertainty). A new field is attached to give the human time of each record (for later data processing use). For example, 191101080030 means 08:00:30 AM, Nov 01, 2019. The field time_zone_offset from the raw data is useless after giving human time and is removed to save storage space. There are about 5000 users in each file. 
- Input files: user name list (from step 1), 60 csv files (from step 1 above)
- Output files: multiple csv files, each csv file contains about 5000 users’ all records over the time period (say 2 months). 

How to run it:  
`python step3_gatherTracesOfEachUser_RemoveDuplicate.py "E:/data" 5000`  
Here, the string `"E:/data"` gives the folder directory of the unzipped data. `5000` gives the batch size, meaning how many users we want to read in to memory for sorting. 

#### Codes in Processing Folder
The folder provides codes of processing the data for extracting stays. It contains 10 py files. Among them, users only need to operate on the main.py, as the other 9 files are called by the main function in the main.py. 

##### [main.py](https://github.com/feilongwang92/app-data/blob/master/processing/main.py "main.py")
- Input files: one of the csv files obtained from step 3 in the preprocessing folder. Recall that the csv file contains 5000 users. The dictionary of the input file is provided in the pdf file “Dictionaries of Cuebiq data and notes of data processing by Feilong.doc”.
- Output files: a csv output file, each containing 5000 users with each user’s stays identified for every day. The number of records after processing will be different as well as the variables contained in the input file and the output file. Each processed record in the output file could represent one of the two: 1) either a transient point, which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a stay (with positive stay_dur). Each record has 12 fields, including several fields that are copies of the original data and additional fields providing stay information (if the record is a stay) such as latitude, longitude, duration, uncertainty radius. Each field is explained in document named “Dictionaries of Cuebiq data and notes of data processing by Feilong”.
- Main.py calls functions from three py files to process each user’s records, including 1) gps_traces_clustering.py; 2) cellular_traces_clustering.py; and 3) combine_stays_phone_gps.py. Each py file is explained below.

How to run it:  
`python main.py "E:/data" "sorted_00.csv" "processed_00.csv" 1000 100 300 0.2 1.0`  
The arguments here are:  
`"E:/data"` gives the work directory, where the input data folder and processed data folder are.  
`"sorted_00.csv"` gives an input data file to be processed.  
`"processed_00.csv"` specifies the file where to write after the data of each user is processed. The file will be under directory `E:/data/processed`. The directory will be created if it does not exist.  
`1000` read how many users from the data into memory; depending on your PC memory size.  
`100` the threshold in meters for partitioning records into gps and cellular traces.  
`300` temporal constraint in seconds to define a stay.  
`0.2` spatial constraint in Km to define a gps stay (e.g., 0.2 Km).  
`1.0` spatial constraint in Km to define a cellular stay (e.g., 1.0 Km).  

##### [gps_traces_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/gps_traces_clustering.py "gps_traces_clustering.py")
The file specifies the function clusterGPS called by main.py. The function is to cluster gps data of one user into stays or identifying it as a transient point. 
- Input of the function: gps records of one user ID. The data is structured in a python dictionary containing records of all days. The key of the dictionary gives a date and the value is a list of raw gps records (with Accuracy/uncertainty radius <= 100meters) on the date. A raw record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: gps processed records (either a stay or a transient point) of the input user ID. The data structure is the same as the input: a python dictionary containing records of all days with the key of the dictionary being a date and its value being a list of processed records on the date. There are more fields (11 fields) than the input, so that the identified stay locations are included. Examples and explanations of a processed record can be found in the pdf file titled “data dictionary for trip_identified by feilong.pdf”. Each processed record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a gps stay (with positive stay_dur). 

##### [cellular_traces_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/cellular_traces_clustering.py "cellular_traces_clustering.py")
The file specifies the function clusterPhone called by main.py. The function is to cluster cellular data of one user. 
- Input of the function: cellular records of one user ID. The data is structured in a dictionary containing records of all days for one user. The key of the dictionary gives a date and the value is a list of raw cellular records (with Accuracy/uncertainty radius > 100meters) on the date. A raw cellular record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: processed cellular records of the input user ID. The data structure is the same as the input: a python dictionary containing records of all days with a key being a date and its value being a list of processed cellular records on the date. There are more fields (11 fields) than the input, including the fields of the identified stay location. Examples and explanations of a processed record can be found in document named “Dictionaries of Cuebiq data and notes of data processing by Feilong”. Each processed record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a cellular stay (with positive stay_dur).

##### [combine_stays_phone_gps.py](https://github.com/feilongwang92/app-data/blob/master/processing/combine_stays_phone_gps.py "combine_stays_phone_gps.py")
The file specifies the function combineGPSandPhoneStops called by main.py. The function is to combine processed gps records and processed cellular data of one user. 
- Input of the function: processed gps records (output of function clusterGPS ) and processed cellular data (output of function clusterPhone) of one user ID. 
- Output of the function: processed records of the input user ID. As the same as the input data, the output data is structured in a python dictionary. A key gives a date and its value gives a list of integrated, processed records on the date. The 11 columns of the output have the same meaning as the input and explanations can be found in document “Dictionaries of Cuebiq data and notes of data processing by Feilong”. Each record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a stay (with positive stay_dur). Here, a stay could come from a cellular stay or a gps stay. 

The following py functions are called into the previous three functions: 1) gps_traces_clustering.py; 2) cellular_traces_clustering.py; and 3) combine_stays_phone_gps.py.

##### [incremental_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/incremental_clustering.py "incremental_clustering.py")
The file specifies the function “cluster_incremental” that is called by cellular_traces_clustering.py, gps_traces_clustering.py and combine_stays_phone_gps.py. 
The function can cluster a list of locations together. It is used when one needs to cluster raw records or identified stays on multiple days based on a specified spatial threshold, so that common stays (e.g., home location) can be identified.
- Input of the function: raw or processed records of one user ID. The data is structured in a python dictionary containing records of all days for a user. The date and the records on the date are a key and its value of the dictionary, respectively.
- Output of the function: processed records of the input user ID. The data structure is the same as the input. As the same as the input data, the output data is structured in a python dictionary. A key gives a date and its value gives a list of integrated, clustered records on the date. There are 11 columns of the output and explanations can be found in “data dictionary for trip_identified by feilong.pdf”. Each record is either a transient point or a stay.

##### [trace_segmentation_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/trace_segmentation_clustering.py "trace_segmentation_clustering.py")
The file specifies the function “cluster_traceSegmentation” called by gps_traces_clustering.py. The function clusters gps locations belong to one user together. It is used when one needs to cluster raw gps records to identify gps stays on multiple days based on a specified temporal and spatial threshold.
- Input of the function: gps records of one user ID. The data is structured in a python dictionary containing records of all days. The key of the dictionary gives a date and the value is a list of raw gps records (with Accuracy/uncertainty radius <= 100meters) on the date. A raw record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: processed records (either a stay or a transient point) of the input user ID. Different from the function clusterGPS, stays identified on different days are distinct and thus need one more step as in clusterGPS to identify common stays. Similarly, the output data structure is the same as the input: a python dictionary containing records of all days with the key of the dictionary being a date and its value being a list of processed records on the date. There are more fields than the input (12 fields in total), as the information of the identified stay locations are included. (Examples and explanations of a processed record can be found in the pdf file titled “data dictionary for trip_identified by feilong.pdf”.) Each processed record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a gps stay (with positive stay_dur). 

##### [class_cluster.py](https://github.com/feilongwang92/app-data/blob/master/processing/class_cluster.py "class_cluster.py")
The file specifies the function “cluster” that defines a python class. The function is called in all clustering algorithms. 
- Input of the function: no input. 
- Output of the function: a python class. Attributes of the class: 1) pList, storing a list of locations (in latitude and longitude) belonging to a cluster; 2) center, storing the center of the cluster in latitude and longitude; 3) radius, the center of the cluster in meters. Methods of the class: 1) addPoint is to add a location in latitude and longitude to pList; 2) updateCenter is to update center; 3) distance_C_point is to compute the Euclidean distance between a location (the input of this function) to the center of the cluster; 4) radiusC is to compute radius of the cluster.

##### [oscillation_type1.py](https://github.com/feilongwang92/app-data/blob/master/processing/oscillation_type1.py "oscillation_type1.py")
The file specifies the function “oscillation_h1_oscill” called by cellular_traces_clustering.py and combine_stays_phone_gps.py. The function is to address oscillation traces in one user’s trajectory. 
- Input of the function: processed records for one user ID. The data is structured in a python dictionary containing records of all days for a user. The date and records on the date are the keys and values of the dictionary, respectively. As noted above, each record is either a transient point or a stay.
- Output of the function: processed records for one user ID with oscillation traces being removed. The data structure is the same as the input. 

##### [distace.py](https://github.com/feilongwang92/app-data/blob/master/processing/distance.py "distace.py")
The file specifies the function “distance”. The function is to compute the distance between two locations and is commonly used in almost every py files. 
- Input of the function: a list of two locations in longitude and latitude.
- Output of the function: a float-type number giving the Euclidean distance between the input two locations in kilometers. 
- A note following a previous discussion: The function computes geodesic distance. The function should not be replaced by a simple Euclidean distance function, as latitude and longitude are not equivalent. Specifically, in the Seattle area, the geodesic distance will increase by about 100 meters if the latitude increases by 0.001, but the geodesic distance will increase by only about 20 meters if the longitude increases by 0.001. And this difference between latitude and longitude should be unique in different areas of the Earth. 

##### [util_func.py](https://github.com/feilongwang92/app-data/blob/master/processing/util_func.py "util_func.py")
The file intends to pack simple functions that are frequently used in processing the data, including  “update_duration” (update stay duration whenever records are modified). 
- Input of update_duration: records of the input user ID. 
- Output of update_duration: records of the input user ID with stay duration updated. 

A test dataset is included in this folder and is organized in folder “test_data”. 
For testing purposes, both the input (example raw data) and output data (processed data) are included. The output data can be compared with your output to identify potential issues in your implementation. 
The test data is in file “anExample”. It contains one user ID and two manually created trajectories on two days, one having 3 trips and the other one having 2 trips. You could find some visualizations of this example data in another document named “workflow of data processing.doc”.

#### Codes in Postprocessing Folder
This folder serves as an example of how to read in the processed data for postprocessing computations, such as inferring home and work locations. 
##### [home_work.py](https://github.com/feilongwang92/app-data/blob/master/postprocessing/home_work.py "home_work.py")
- Input files: one of the csv files obtained from the processing folder. Recall that such a csv file contains processed observations of 5000 users.
- Output files: There will be two csv files. One contains home locations and the other contains work locations. Each row of the home/work file gives the home/work location of one user, in the form of longitude and latitude. 

How to run it:
`python home_work.py "E:/data/processed/processed_00.csv" 1000`
Here, `"E:/data/processed/processed_00.csv"` gives the name of a file containing a part of processed data. `1000` gives the batch size, meaning how many users we want to read into memory for computation.  

Notes of running and understanding the codes:
- Codes are written in python 2.7; do remember that python codes are sensitive to package versions. The codes are tested in an environment of anaconda2-4.2.0. So the easiest way of duplicating the computation environment is to install [anaconda2-4.2.0](https://repo.anaconda.com/archive/ "anaconda2-4.2.0"). Note, it is not the latest anaconda version. It is found that the outputs could be different if an environment other than anaconda2-4 is used; it is not clear which package dependency raises this issue.
- For more understandings of the algorithms underlying these codes: Refer to a report “Promises of transportation big data, 2019” that is a deliverable of the FHWA project in 2018. Refer to the paper led by Feilong Wang “extracting trip ends from multi-sourced data, 2019” 
- Additional notes and tips of running the codes can be found at the end of document named “Dictionaries of Cuebiq data and notes of data processing by Feilong.doc”
