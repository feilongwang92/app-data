**Table of Content**
- [Introduction to the data structure of raw app-based data](#introduction-to-the-data-structure-of-raw-app-based-data)
  * [Raw Data Folders](#raw-data-folders)
  * [Raw Data Files](#raw-data-files)
- [Codes in Preprocessing Folder:](#codes-in-preprocessing-folder-)
  * [step1_unzip_combine_file.py](#step1-unzip-combine-filepy)
  * [step2_getAllUserId.py](#step2-getalluseridpy)
  * [step3_gatherTracesofEachUser_removeDuplicate.py](#step3-gathertracesofeachuser-removeduplicatepy)
- [Codes in Processing Folder](#codes-in-processing-folder)
  * [main.py](#mainpy)
    + [gps_traces_clustering.py](#gps-traces-clusteringpy)
    + [cellular_traces_clustering.py](#cellular-traces-clusteringpy)
    + [combine_stays_phone_gps.py](#combine-stays-phone-gpspy)
    + [incremental_clustering.py](#incremental-clusteringpy)
    + [trace_segmentation_clustering.py](#trace-segmentation-clusteringpy)
    + [class_cluster.py](#class-clusterpy)
    + [oscillation_type1.py](#oscillation-type1py)
    + [distace.py](#distacepy)
    + [util_func.py](#util-funcpy)
- [Codes in Postprocessing Folder](#codes-in-postprocessing-folder)
  * [home_work.py](#home-workpy)
- [Notes of running and understanding the codes](#notes-of-running-and-understanding-the-codes)



The codes are in three folders, including the preprocessing, processing, and postprocessing folders. 

- The codes in the preprocessing folder are to combine together records belonging to each user and contained many tiny files, sort records by time and remove duplicated records. 

- The codes in the processing folder are to extract trip ends from the data. The methodology based on which the codes are developed can be found in the recently published paper "[*Extracting trips from multi-sourced data for mobility pattern analysis: An app-based data example*](https://www.sciencedirect.com/science/article/pii/S0968090X18316085)". 

- The codes in the postprocessing folder serve examples of using the processing data for mobility pattern analyses.





In the following, codes in each folder are introduced in detail. Comments embedded in the codes are also helpful to understand the codes. A workflow for processing the data is introduced in file "Workflow of data processing". You may find it helpful to understand the codes in the processing folder. 

At the end of this document, instructions for deploying the computational environment are specified. Note that codes are in **Python 2.7**. The outcomes could be sensitive to the computational environment. 

##### Introduction to the data structure of raw app-based data

To understand the preprocessing steps, you first need to know how raw data are organized into small files and folders by the data vendor.
###### Raw Data Folders
Raw data are sorted into a series of gzipped files (introduced in the following), partitioned into folders by date. The folder names will represent the day on which the data was processed by Cubiq. For example,
	2018010100 - meaning the data was processed on January 1, 2018
	2018010200 - meaning the data was processed on January 2, 2018
	2018010300 - meaning the data was processed on January 3, 2018
According to emails from Cuebiq, data are processed at 12AM UTC and there can also be a certain lag in the data. Cuebiq receives the data as it is batched on a device before being sent to Cuebiq’s servers, therefore the timestamps in each dated folder may not represent only that day and could potentially include some data from additional dates.  The rule of thumb is that if each data folder will have 90+% of data for a given day looking at the data for that day and the following day. So, for example, 90+% of data for January 1, 2018 would be found in folders:
	2018010100 - meaning the data was processed on January 1, 2018
	2018010200 - meaning the data was processed on January 2, 2018

The code block below shows how raw data are organized in folders, as introduced above. Each day is a folder containing many smaller gzipped files. The size of each csv file is similar. It is possible that a single user have the same, similar or different records showing in multiple files for the same day. 


> **Code block 1.** Directory structure of the raw data. Organized by the data vendor, records of each day are within one folder (e.g., 2019110100) but not in one file. In each folder, there are hundreds of small zipped, csv files, each containing thousands of records belonging to multiple users. You need to create a folder, name is "raw" and put the raw data under the folder. To preprocessing the raw data, you will input the directory ("data" in this example) where the "raw" folder is, so that the codes will find the raw data and store preprocessed data under "data". 

```bash
├── data
│   ├── raw
│   │   ├── 2019110100
│   │   │   ├── part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   ├── part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   └── ...
│   │   ├── 2019110200
│   │   │   ├── part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   ├── part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   └── ...
│   │   └── ...
```

###### Raw Data Files
The actual fields in the data are structured as below (fields are separated by TAB); Each small gzipped file is in csv format; each row gives an observation, containing 7 columns/fields, which are seprated by TAB. Table 1 gives a sample of synthetic observations and Table 2 explains each field of an observation. 

**Table 1. A sample of raw data.**

|Timestamp | ID | ID Type | Latitude | Longitude | Accuracy | Time zone offset |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
|1491673511 | 560b2…1703a253f | 0 | 41.24319 | -80.4503 | 28 | -14400|
|1491616021 | 80308…873dc16c3 | 0 | 35.10808 | -92.4338 | 110 | -18000|
|1491616466 | c248c…7321bde86 | 1 | 40.25225 | -74.7267 | 30 | -14400|

**Table 2. Description of each field in raw data**

| <div style="width:100px">Data field</div> | Description                           |
| --------------------------------------- | ------------------------------------- |
|Timestamp | UTC timestamp (in Unix) regarding the data point.|
|ID | Unique ID hashed with Cuebiq’s proprietary algorithm |
|ID Type | Device OS representation (0: Android; 1: iOS; Nothing: Unknown) | 
|Latitude | Latitude of location | 
|Longitude | Longitude of location | 
|Accuracy | Data point accuracy/uncertainty radius expressed in meters | 
|Time zone offset | Time zone offset from UTC | 


#### Codes in Preprocessing Folder: 
There are three python files in the preprocessing folder; each is introduced below. 

##### [step1_unzip_combine_file.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step1_unzip_combine_file.py "step1_unzip_combine_file.py")

Codes in this file is to process the zipped files originally provided, unzip them, and put them into another folder as a user-specified code. 
- Input: the directory where the raw data files are stored. 
- Output: a new folder "unzipped" under the input directory containing multiple csv files. In the folder, there will be one csv file containing all the users for one day. For example, if the time period is 60 days, there will be 60 csv files generated. 

How to run it:  
`python step1_unzip_combine_file.py "E:/data"`  
Here, the string `"E:/data"` gives the directory of the raw folder.  Again, you need to create a folder, name is "raw" and put the raw data under the "raw" folder (as show by the structure in code block 1). The directory of your input ("data" in this example) is where the "raw" folder is. The codes will search your directory and find the "raw" data folder. 

After the small gzipped files in each folder is unzipped, data in one folder becomes a csv file. After step 1, the data directory should looks like the one in code block 2 (see below). Compare with the directory in code block 1, a new folder "unzipped" is created and each file in "unzipped" is a csv file.

> **Code block 2.** Directory structure after preprocessing step 1.

```bash
├── data
│   ├── raw
│   │   ├── 2019110100
│   │   │   ├── part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   ├── part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   └── ...
│   │   ├── 2019110200
│   │   │   ├── part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   ├── part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   └── ...
│   │   └── ...
│   ├── unzipped
│   │   ├── 20191101.csv
│   │   ├── 20191101.csv
│   │   └── ...
```

##### [step2_getAllUserId.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step2_getAllUserId.py "step2_getAllUserId.py") 

Extract user ids from the output files from the previous step. 
- Input: the directory where the data files are stored. The codes will find the "unzipped" folder and the data files that are outputted from the previous step.
- Output: a csv file containing all user ids. The file is stored under the input directory "data"; each row gives one user ID.

How to run it:  
`python step2_getAllUserId.py "E:/data"`  
Here, the string `"E:/data"` gives the folder directory of the unzipped data. 

After step 2, your data directory should contain a new csv file "usernamelist.csv", which appears under "data". 

> **Code block 3.** Directory structure after preprocessing step 2. 

```bash
├── data
│   ├── raw
│   │   ├── 2019110100
│   │   │   ├── part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   ├── part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   └── ...
│   │   ├── 2019110200
│   │   │   ├── part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   ├── part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   └── ...
│   │   └── ...
│   ├── unzipped
│   │   ├── 20191101.csv
│   │   ├── 20191101.csv
│   │   └── ...
└── usernamelist.csv
```

##### [step3_gatherTracesofEachUser_removeDuplicate.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step3_gatherTracesOfEachUser_RemoveDuplicate.py "step3_gatherTracesofEachUser_removeDuplicate.py") 

Take in the previous output files, for each user, scan through all unzipped files and append observations for the same user together, so that for a single user, all his/her records will be contained in a single file. Sort all records for each user by time and remove duplicates (if multiple records have the same time but different location information, you retain the record with lower uncertainty). 

- Input: Two arguments: 1) The data directory where the user name list (from step 2) and unzipped data files (from step 1 above) are stored. The codes will search for "usernamelist.csv" and folder "unzipped". 2) Batch size (e.g., 5000). To avoid memory overflow, users are split into small batches and one batch of users are read in memory for preprocessing at one time.  
- Output: A new folder "sorted" and multiple csv files under the folder. Each csv file contains about 5000 (determined by the input "batch size") users' observations over the time period (say 2 months). 

How to run it:  
`python step3_gatherTracesOfEachUser_RemoveDuplicate.py "E:/data" 5000`  
Here, the string `"E:/data"` gives the folder directory of the unzipped data. `5000` gives the batch size, meaning how many users we want to read in to memory for sorting. 

Sorted data are cut into multiple small files, each of which contains 5000 users (this number is the batch size as your input). IDs are shuffled before being split into small files. That is, each file contains a random sample of users. Each file is in CSV format; each row gives an observation, seperated by TAB. Table 3 gives a sample:

**Table 3. A sample of sorted data.**

|Timestamp | ID | ID Type | Latitude | Longitude | Accuracy | Human_time |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
|1491673511 | 560b2…1703a253f | 0 | 41.24319 | -80.4503 | 28 | 170408134511|
|1491616021 | 80308…873dc16c3 | 0 | 35.10808 | -92.4338 | 110 | 170407204701|
|1491616466 | c248c…7321bde86 | 1 | 40.25225 | -74.7267 | 30 | 170407215426|

As shown in Table 3, an additional column/field is attached to give the human time of each record. It is named as “human_time”, which is a translation of the Unix timestamp of each record to local time. For example, the record with unix timestamp 1491673511 is given human_time 170408134511, meaning 2017/04/08 13:45:11. The translation uses python package `time` and considers the time zone offset: `time.strftime("%y%m%d%H%M%S", time.gmtime(Timestamp + timezone_offset))`. This additional field is for the convenience of further computations. 
The field time_zone_offset from the raw data is removed to save storage space. It is useless once we have “human_time”, which is already in the local time zone. 

At the end of the three steps, your work directory should look like the one in the following. Notice that a new folder "sorted" is created; each csv file in the folder contains the observations of a part of users (e.g., 5000 in the example).  

> **Code block 3.** The data directory after the three preprocessing steps.
```bash
├── data
│   ├── raw
│   │   ├── 2019110100
│   │   │   ├── part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   ├── part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
│   │   │   └── ...
│   │   ├── 2019110200
│   │   │   ├── part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   ├── part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
│   │   │   └── ...
│   │   └── ...
│   ├── unzipped
│   │   ├── 20191101.csv
│   │   ├── 20191101.csv
│   │   └── ...
│   ├── sorted
│   │   ├── sorted_00.csv
│   │   ├── sorted_01.csv
│   │   └── ...
└── usernamelist.csv
```


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

Table 4 shows a sample of (synthetic) processed data. Each record and its 12 fields are described in Table 5. One processed data file contains the same set of users in the input file. Therefore, one file has 5000 users.
**Table 4. Data sample of processed data**

|Unix_start_t | ID | ID_Type | Orig_lat | Orig_long | Orig_unc | Stay_lat | Stay_long | Stay_unc | Stay_dur | Stay_label | Human_start_t|
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | 
|1588778435 | 3dd3bc7f67 | 1 | 47.660252 | -122.316416 | 60 | 47.660496 | -122.3157499 | 60 | 1080 | stay3 | 200506082035|
|1588779575 | 3dd3bc7f67 | 1 | 47.659797 | -122.313198 | 30 | -1 | -1 | -1 | -1 | -1 | 200506083935|
|1588779635 | 3dd3bc7f67 | 1 | 47.659797 | -122.313112 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084035|
|1588779695 | 3dd3bc7f67 | 1 | 47.659797 | -122.312066 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084135|
|1588779755 | 3dd3bc7f67 | 1 | 47.659753 | -122.310049 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084235|
|1588779815 | 3dd3bc7f67 | 1 | 47.659565 | -122.307173 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084335|
|1588779875 | 3dd3bc7f67 | 1 | 47.658792 | -122.307624 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084435|
|1588779935 | 3dd3bc7f67 | 1 | 47.65747 | -122.307946 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084535|
|1588779995 | 3dd3bc7f67 | 1 | 47.656182 | -122.309321 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084635|
|1588780055 | 3dd3bc7f67 | 1 | 47.653401 | -122.307242 | 30 | -1 | -1 | -1 | -1 | -1 | 200506084735|
|1588786220 | 3dd3bc7f67 | 1 | 47.651771 | -122.30443 | 300 | 47.6524318 | -122.3040553 | 397 | 2400 | stay0 | 200506103020|
|1588796725 | 3dd3bc7f67 | 1 | 47.654627 | -122.304974 | 25 | -1 | -1 | -1 | -1 | -1 | 200506132525|
|1588797025 | 3dd3bc7f67 | 1 | 47.664434 | -122.298189 | 50 | 47.6645295 | -122.2981445 | 0 | 3000 | stay1 | 200506133025|
|1588864835 | 3dd3bc7f67 | 1 | 47.661252 | -122.315416 | 60 | 47.660496 | -122.3157499 | 60 | 1260 | stay3 | 200507082035|
|1588866155 | 3dd3bc7f67 | 1 | 47.660753 | -122.312049 | 5 | -1 | -1 | -1 | -1 | -1 | 200507084235|
|1588866215 | 3dd3bc7f67 | 1 | 47.660565 | -122.309173 | 5 | -1 | -1 | -1 | -1 | -1 | 200507084335|
|1588866275 | 3dd3bc7f67 | 1 | 47.659792 | -122.309624 | 5 | -1 | -1 | -1 | -1 | -1 | 200507084435|
|1588866335 | 3dd3bc7f67 | 1 | 47.65847 | -122.309946 | 5 | -1 | -1 | -1 | -1 | -1 | 200507084535|
|1588866395 | 3dd3bc7f67 | 1 | 47.657182 | -122.311321 | 5 | -1 | -1 | -1 | -1 | -1 | 200507084635|
|1588866455 | 3dd3bc7f67 | 1 | 47.654401 | -122.309242 | 5 | -1 | -1 | -1 | -1 | -1 | 200507084735|
|1588883125 | 3dd3bc7f67 | 1 | 47.655627 | -122.303974 | 25 | -1 | -1 | -1 | -1 | -1 | 200507132525|
|1588883428 | 3dd3bc7f67 | 1 | 47.658034 | -122.304189 | 50 | 47.658073 | -122.3041392 | 0 | 2397 | stay2 | 200507133025|

**Table 5.** Description of each field in processed data

| <div style="width:100px">Data field</div> | Description                           |
| --------------------------------------- | ------------------------------------- |
|Unix_start_t | The first timestamp when this stay is observed; if this record is a passingby record, it gives the timestamp of this passingby record.  |
|ID | User ID |
|ID_type | OS type of devices in original data; now modified as “addedphonestay” if it is stay acquired after combing cellular and gps data |
|Orig_lat / Orig_long / Orig_unc | Latitude / Longitude / Location uncertainty (in meters), in original data |
|Stay_lat / Stay_long / Stay_unc / Stay_dur |  Latitude / Longitude / uncertainty(meters) / duration(seconds) of identified stay; if not a stay but a passing point, marked as “-1”|
|Stay_label | A label is given to each stay. The label is unique for a stay location belonging to one user in the entire study period. There is no order when labeling the locations (just label a location with 0 when it is first seen).|
|Human_start_t | Translation of unix_start_t; for reading and later calculation convenience; 200507133025 means 2020/05/07 13:30:25 PM.|


###### [gps_traces_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/gps_traces_clustering.py "gps_traces_clustering.py")
The file specifies the function clusterGPS called by main.py. The function is to cluster gps data of one user into stays or identifying it as a transient point. 
- Input of the function: gps records of one user ID. The data is structured in a python dictionary containing records of all days. The key of the dictionary gives a date and the value is a list of raw gps records (with Accuracy/uncertainty radius <= 100meters) on the date. A raw record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: gps processed records (either a stay or a transient point) of the input user ID. The data structure is the same as the input: a python dictionary containing records of all days with the key of the dictionary being a date and its value being a list of processed records on the date. There are more fields (11 fields) than the input, so that the identified stay locations are included. Examples and explanations of a processed record can be found in the pdf file titled “data dictionary for trip_identified by feilong.pdf”. Each processed record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a gps stay (with positive stay_dur). 

###### [cellular_traces_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/cellular_traces_clustering.py "cellular_traces_clustering.py")
The file specifies the function clusterPhone called by main.py. The function is to cluster cellular data of one user. 
- Input of the function: cellular records of one user ID. The data is structured in a dictionary containing records of all days for one user. The key of the dictionary gives a date and the value is a list of raw cellular records (with Accuracy/uncertainty radius > 100meters) on the date. A raw cellular record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: processed cellular records of the input user ID. The data structure is the same as the input: a python dictionary containing records of all days with a key being a date and its value being a list of processed cellular records on the date. There are more fields (11 fields) than the input, including the fields of the identified stay location. Examples and explanations of a processed record can be found in document named “Dictionaries of Cuebiq data and notes of data processing by Feilong”. Each processed record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a cellular stay (with positive stay_dur).

###### [combine_stays_phone_gps.py](https://github.com/feilongwang92/app-data/blob/master/processing/combine_stays_phone_gps.py "combine_stays_phone_gps.py")
The file specifies the function combineGPSandPhoneStops called by main.py. The function is to combine processed gps records and processed cellular data of one user. 
- Input of the function: processed gps records (output of function clusterGPS ) and processed cellular data (output of function clusterPhone) of one user ID. 
- Output of the function: processed records of the input user ID. As the same as the input data, the output data is structured in a python dictionary. A key gives a date and its value gives a list of integrated, processed records on the date. The 11 columns of the output have the same meaning as the input and explanations can be found in document “Dictionaries of Cuebiq data and notes of data processing by Feilong”. Each record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a stay (with positive stay_dur). Here, a stay could come from a cellular stay or a gps stay. 

The following py functions are called into the previous three functions: 1) gps_traces_clustering.py; 2) cellular_traces_clustering.py; and 3) combine_stays_phone_gps.py.

###### [incremental_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/incremental_clustering.py "incremental_clustering.py")
The file specifies the function “cluster_incremental” that is called by cellular_traces_clustering.py, gps_traces_clustering.py and combine_stays_phone_gps.py. 
The function can cluster a list of locations together. It is used when one needs to cluster raw records or identified stays on multiple days based on a specified spatial threshold, so that common stays (e.g., home location) can be identified.
- Input of the function: raw or processed records of one user ID. The data is structured in a python dictionary containing records of all days for a user. The date and the records on the date are a key and its value of the dictionary, respectively.
- Output of the function: processed records of the input user ID. The data structure is the same as the input. As the same as the input data, the output data is structured in a python dictionary. A key gives a date and its value gives a list of integrated, clustered records on the date. There are 11 columns of the output and explanations can be found in “data dictionary for trip_identified by feilong.pdf”. Each record is either a transient point or a stay.

###### [trace_segmentation_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/trace_segmentation_clustering.py "trace_segmentation_clustering.py")
The file specifies the function “cluster_traceSegmentation” called by gps_traces_clustering.py. The function clusters gps locations belong to one user together. It is used when one needs to cluster raw gps records to identify gps stays on multiple days based on a specified temporal and spatial threshold.
- Input of the function: gps records of one user ID. The data is structured in a python dictionary containing records of all days. The key of the dictionary gives a date and the value is a list of raw gps records (with Accuracy/uncertainty radius <= 100meters) on the date. A raw record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: processed records (either a stay or a transient point) of the input user ID. Different from the function clusterGPS, stays identified on different days are distinct and thus need one more step as in clusterGPS to identify common stays. Similarly, the output data structure is the same as the input: a python dictionary containing records of all days with the key of the dictionary being a date and its value being a list of processed records on the date. There are more fields than the input (12 fields in total), as the information of the identified stay locations are included. (Examples and explanations of a processed record can be found in the pdf file titled “data dictionary for trip_identified by feilong.pdf”.) Each processed record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a gps stay (with positive stay_dur). 

###### [class_cluster.py](https://github.com/feilongwang92/app-data/blob/master/processing/class_cluster.py "class_cluster.py")
The file specifies the function “cluster” that defines a python class. The function is called in all clustering algorithms. 
- Input of the function: no input. 
- Output of the function: a python class. Attributes of the class: 1) pList, storing a list of locations (in latitude and longitude) belonging to a cluster; 2) center, storing the center of the cluster in latitude and longitude; 3) radius, the center of the cluster in meters. Methods of the class: 1) addPoint is to add a location in latitude and longitude to pList; 2) updateCenter is to update center; 3) distance_C_point is to compute the Euclidean distance between a location (the input of this function) to the center of the cluster; 4) radiusC is to compute radius of the cluster.

###### [oscillation_type1.py](https://github.com/feilongwang92/app-data/blob/master/processing/oscillation_type1.py "oscillation_type1.py")
The file specifies the function “oscillation_h1_oscill” called by cellular_traces_clustering.py and combine_stays_phone_gps.py. The function is to address oscillation traces in one user’s trajectory. 
- Input of the function: processed records for one user ID. The data is structured in a python dictionary containing records of all days for a user. The date and records on the date are the keys and values of the dictionary, respectively. As noted above, each record is either a transient point or a stay.
- Output of the function: processed records for one user ID with oscillation traces being removed. The data structure is the same as the input. 

###### [distace.py](https://github.com/feilongwang92/app-data/blob/master/processing/distance.py "distace.py")
The file specifies the function “distance”. The function is to compute the distance between two locations and is commonly used in almost every py files. 
- Input of the function: a list of two locations in longitude and latitude.
- Output of the function: a float-type number giving the Euclidean distance between the input two locations in kilometers. 
- A note following a previous discussion: The function computes geodesic distance. The function should not be replaced by a simple Euclidean distance function, as latitude and longitude are not equivalent. Specifically, in the Seattle area, the geodesic distance will increase by about 100 meters if the latitude increases by 0.001, but the geodesic distance will increase by only about 20 meters if the longitude increases by 0.001. And this difference between latitude and longitude should be unique in different areas of the Earth. 

###### [util_func.py](https://github.com/feilongwang92/app-data/blob/master/processing/util_func.py "util_func.py")
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

#### Notes of running and understanding the codes

**Notes of preprocessing raw data**

- some unexpected records: some raw records may have '\N' value in their “accuracy” field; 

- duplicated records can be in two forms: 1) two records are the same in terms of all fields; 2) two records have the same timestamp and latitude and longitude coordinates, but they have different location accuracy; 

- A note of loading data to database, if you use a database instead of operating on csv files directly: accuracy of some records could be as large as 562119 meters (should be outliers; be careful when loading data into a database, as in a database, an integer 562119 is loaded as 32768 using a SmallInt datatype); 

- longitude/latitude in some raw records have no decimal place (e.g., 45	-125); be careful when you deal with decimal places. 

- Some records have a time zone that is different from your study area. For example, the Puget Sound region data have records that are not at Pacific Standard Time. Specifically, for these records, values at time-zone field (the last column) can be -36000, which stands for Alaska time (2 hours later than PST). (Such unexpected records are loaded as -32768 in a database if SmallInt is used.)

**Tips for Addressing “out of memory” issue:**

- If your machine gets a small memory, you can process observations belongs to a small batch of IDs: Read 5000 unique IDs (or 2000 IDs), get observations of these IDs from disk to memory, conduct computations, save results on disk, release memory and read next 5000 IDs. You may find that sorted and processed data have already been cut into files, each of which contains 5000 IDs. So you can read in and process these data files one by one.

- Does using a database improve processing speed compared with working on csv files directly? Based on my experiments, using a database may not be a good idea in our cases. Time-saving from using a database is limited as it takes much time for just loading all files into a database table and indexing the table, although it is relatively fast to fetch observations belonging to one ID after the data is loaded. The use of databases has its advantages when we need some frequent data manipulations, for example, when we need to frequently identify and mute one specific ID. For sorting and processing all observations, the use of the database has no clear advantage as the data are processed in batches. 

**Notes for processing data (e.g., identification of trip ends)**

- Most of IDs can be processed quickly, but some “outlier” IDs, who have a large number of records (see an example below), require long computation time. In the worst case, it takes about one day to process such outlier IDs. You may find that one ID has 77,178 records: f8afa76b6aaaa5cd0c07171f96a2caf9d29911018b44a149d02df1ac910ef4f8 in the file part201805.csv in PSRC data from Jan to March of 2018. 

- Tips of addressing “outliers”: when applying multi-processing, sort your IDs into a queue in the reverse order according to the number of observations of the IDs. In this way, the ID with the most number of observations is put at the top of the queue and is processed first.  Use the function pool.apply_async instead of pool.map in Python (see python document for the differences between the two). 

- Codes of some functions seem necessarily complicated. They are coded to save calculation time. For example, originally, it takes a few lines in function diameterExceedCnstr, which is to find out whether the diameter of a cluster (defined as the longest distance between any two locations in the cluster) exceeds 200 meters. For saving computation time, the function is rewritten by applying some additional heuristic rules (see comments in function diameter). 


- Codes are written in python 2.7; do remember that python codes are sensitive to package versions. The codes are tested in an environment of anaconda2-4.2.0. So the easiest way of duplicating the computation environment is to install [anaconda2-4.2.0](https://repo.anaconda.com/archive/ "anaconda2-4.2.0"). Note, it is not the latest anaconda version. It is found that the outputs could be different if an environment other than anaconda2-4 is used; it is not clear which package dependency raises this issue.

- For more understandings of the algorithms underlying these codes: Refer to a report “Promises of transportation big data, 2019” that is a deliverable of the FHWA project in 2018. Refer to the paper led by Feilong Wang “extracting trip ends from multi-sourced data, 2019” 
- Additional notes and tips of running the codes can be found at the end of document named “Dictionaries of Cuebiq data and notes of data processing by Feilong.doc”
