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

- The codes in the postprocessing folder serve examples of using the processed data for mobility pattern analyses.

In the following, codes in each folder are introduced in detail. For each code file (python file), we introduce its purpose, input, output and provde an example to execute it. 

Comments embedded in the python files (following the hyperlinks) should be helpful in understanding the codes. Workflow for processing the data is introduced in file "[Workflow of data processing.pdf](https://github.com/feilongwang92/app-data/blob/master/processing/Workflow%20of%20data%20processing.pdf "Workflow of data processing.pdf")". You may find it helpful to understand the codes in the processing folder. 

At the end of this document, instructions for deploying the computational environment are specified. Note that codes are written in **Python 2.7**. The outcomes could be sensitive to the computational environment. 

## Introduction to the data structure of raw app-based data

To understand the preprocessing steps, you first need to know how raw data are organized into small files and folders by the data vendor.
### Raw Data Folders
Raw data are sorted into a series of gzipped files (introduced in the following), partitioned into folders by date. The folder names will represent the day on which the data was processed by Cubiq. For example,
	2018010100 - meaning the data was processed on January 1, 2018
	2018010200 - meaning the data was processed on January 2, 2018
	2018010300 - meaning the data was processed on January 3, 2018
According to emails from the data vendor, data are processed at 12AM UTC and there can also be a certain lag in the data. The data vendor receives the data as it is batched on a device before being sent to the data vendor's servers. Therefore the timestamps in each dated folder may not represent only that day and could potentially include some data from additional dates.  The rule of thumb is that if each data folder will have 90+% of data for a given day looking at the data for that day and the following day. So, for example, 90+% of data for January 1, 2018 would be found in folders:
	2018010100 - meaning the data was processed on January 1, 2018
	2018010200 - meaning the data was processed on January 2, 2018

The code block below shows how raw data are organized in folders, as introduced above. Each day is a folder containing many smaller gzipped files. The size of each csv file is similar. It is possible that a single user have the same, similar or different records showing in multiple files for the same day. 


> **Code block 1.** Directory structure of the raw data. Organized by the data vendor, records of each day are within one folder (e.g., 2019110100) but not in one file. In each folder, there are hundreds of small zipped csv files, each containing thousands of records belonging to multiple users. You need to create a folder, name it "raw" and put the raw data under the folder. Later, to preprocessing the raw data, you will input the directory ("data" in this example) that includes the "raw" folder, so that the programs will find the raw data and store outputted data under "data". 

```bash
+-- data
¦   +-- raw
¦   ¦   +-- 2019110100
¦   ¦   ¦   +-- part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- 2019110200
¦   ¦   ¦   +-- part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- ...
```

### Raw Data Files
Each small gzipped file is in csv format; each row gives an observation, containing 7 columns/fields, which are separated by TAB. Table 1 gives a sample of synthetic observations, and Table 2 explains each field of observations. 

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
|ID | Unique ID hashed with the data vendor’s proprietary algorithm |
|ID Type | Device OS representation (0: Android; 1: iOS; Nothing: Unknown) | 
|Latitude | Latitude of location | 
|Longitude | Longitude of location | 
|Accuracy | Data point accuracy/uncertainty radius expressed in meters | 
|Time zone offset | Time zone offset from UTC | 


## Codes in Preprocessing Folder: 
There are three python files in the preprocessing folder; each is introduced below. 

### [step1_unzip_combine_file.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step1_unzip_combine_file.py "step1_unzip_combine_file.py")

Codes in this file is to process the zipped files originally provided, unzip them, and put them into another folder "unzipped".  
- Input: the directory where the raw data files are stored. 
- Output: a new folder "unzipped" is created and appears under the input directory; the folder contains multiple csv files, each of which contains all the users for one day. For example, if the time period is 60 days, there will be 60 csv files generated.   

How to run it:  
`python step1_unzip_combine_file.py "E:/data"`  
Here, the string `"E:/data"` gives the directory of the raw folder.  Again, you need to create a folder, name it "raw" and put the raw data under the "raw" folder (as shown by the structure in code block 1). Your input directory ("data" in this example) is the parent directory that includes the "raw" folder is. The codes will search your input directory and find the "raw" data folder. 

After the small gzipped files in each folder are unzipped, data in one folder becomes a csv file. After step 1, the data directory should look like the one in code block 2 (see below). Compare with the directory in code block 1, a new folder "unzipped" is created and each file in "unzipped" is a csv file.

> **Code block 2.** Directory structure after preprocessing step 1.

```bash
+-- data
¦   +-- raw
¦   ¦   +-- 2019110100
¦   ¦   ¦   +-- part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- 2019110200
¦   ¦   ¦   +-- part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- ...
¦   +-- unzipped
¦   ¦   +-- 20191101.csv
¦   ¦   +-- 20191101.csv
¦   ¦   +-- ...
```

### [step2_getAllUserId.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step2_getAllUserId.py "step2_getAllUserId.py") 

Extract unique user IDs from the output files from the previous step and write the list of IDs to disk.
- Input: the directory where the data files are stored. The codes will find the "unzipped" folder and the data files that are outputted from the previous step.
- Output: a csv file containing all user ids. The file appears under the input directory; each row gives one user ID.

How to run it:  
`python step2_getAllUserId.py "E:/data"`  
Here, the string `"E:/data"` gives the parent directory that includes folder "unzipped", which contains the unzipped data files. 

After step 2, your data directory should contain a new csv file “usernamelist.csv” (see code block 3 below). 

> **Code block 3.** Directory structure after preprocessing step 2. 

```bash
+-- data
¦   +-- raw
¦   ¦   +-- 2019110100
¦   ¦   ¦   +-- part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- 2019110200
¦   ¦   ¦   +-- part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- ...
¦   +-- unzipped
¦   ¦   +-- 20191101.csv
¦   ¦   +-- 20191101.csv
¦   ¦   +-- ...
+-- usernamelist.csv
```

### [step3_gatherTracesofEachUser_removeDuplicate.py](https://github.com/feilongwang92/app-data/blob/master/preprocessing/step3_gatherTracesOfEachUser_RemoveDuplicate.py "step3_gatherTracesofEachUser_removeDuplicate.py") 

Take in the previous output files, for each user, scan through all unzipped files and append observations for the same user together, so that for a single user, all his/her records will be contained in a single file. Sort all records for each user by time and remove duplicates (if multiple records have the same time but different location information, we retain the record with lower uncertainty). 

- Input: Two arguments: 1) The data directory where the user name list (from step 2) and unzipped data files (from step 1 above) are stored. Given the parent directory, the program will search for "usernamelist.csv" and folder "unzipped". 2) Batch size (e.g., 5000). In order to avoid memory overflow, users are split into small batches and only one batch of users are read in memory for preprocessing at one round of computation.   
- Output: A new folder "sorted" and multiple csv files under the folder. Each csv file contains about 5000 (determined by the input "batch size") users' observations over the time period (say 2 months). 

How to run it:  
`python step3_gatherTracesOfEachUser_RemoveDuplicate.py "E:/data" 5000`  
Here, the string `"E:/data"` gives the folder directory of the unzipped data. `5000` gives the batch size, meaning we want to read in 5000 users to memory for sorting in one round of computation. 

Sorted data are cut into multiple small files, each of which contains 5000 users (this number is the batch size as your input). IDs are shuffled before being split into small files. That is, each file contains a random sample of users. Each file is in CSV format; each row gives an observation, separated by TAB. Table 3 gives a sample:

**Table 3. A sample of sorted data.**

|Timestamp | ID | ID Type | Latitude | Longitude | Accuracy | Human_time |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
|1491673511 | 560b2…1703a253f | 0 | 41.24319 | -80.4503 | 28 | 170408134511|
|1491616021 | 80308…873dc16c3 | 0 | 35.10808 | -92.4338 | 110 | 170407204701|
|1491616466 | c248c…7321bde86 | 1 | 40.25225 | -74.7267 | 30 | 170407215426|

As shown in Table 3, an additional column/field "Human_time" is attached to give the human time of each record. It is a translation of the Unix timestamp of each record to local time. For example, the record with unix timestamp 1491673511 is given human_time 170408134511, meaning 2017/04/08 13:45:11. The translation uses python package `time` and considers the time zone offset: `time.strftime("%y%m%d%H%M%S", time.gmtime(Timestamp + timezone_offset))`. This additional field is for the convenience of further computations. 
The field time_zone_offset from the raw data is removed to save storage space. It is useless once we have “human_time”, which is already in the local time zone. 

At the end of the three steps, your work directory should look like the one in the following. Notice that a new folder "sorted" is created; each csv file in the folder contains the observations of a part of users (e.g., 5000 in the example).  

> **Code block 3.** The data directory after the three preprocessing steps.
```bash
+-- data
¦   +-- raw
¦   ¦   +-- 2019110100
¦   ¦   ¦   +-- part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- 2019110200
¦   ¦   ¦   +-- part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- ...
¦   +-- unzipped
¦   ¦   +-- 20191101.csv
¦   ¦   +-- 20191101.csv
¦   ¦   +-- ...
¦   +-- sorted
¦   ¦   +-- sorted_00.csv
¦   ¦   +-- sorted_01.csv
¦   ¦   +-- ...
+-- usernamelist.csv
```


## Codes in Processing Folder
The folder provides codes for processing the data (i.e., extracting stays from app data). It contains 10 py files. Among them, you only need to work with `main.py`, as it calls the other 9 files in this folder.   

### [main.py](https://github.com/feilongwang92/app-data/blob/master/processing/main.py "main.py")

Extract trips from app-based data following the “Divide, Conquer and Integrate” (DCI) framework proposed by ([Wang et al. 2019](http://www.sciencedirect.com/science/article/pii/S0968090X18316085 "Wang et al. 2019")).   
- Input: the input should include the data file to be processed and several parameters that are related to the definitions of cellular and gps stays, as listed in Table 5.  Also see an example below for better understanding. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Table 4.** A list of input to `main.py`

| <div style="width:100px">Input</div> | Description                           |
| :------------ | :------------ |
|work_dir | the folder where we store data, including |
|file2process | One of the csv files in folder `sorted` obtained from the preprocessing. Recall that the csv file contains 5000 users.  |
|output2file | specify where to write the processed data|
|batchsize | read how many users from the data into memory; depending on your PC memory size (e.g., 1000 users)|
|spat_cell_split | the threshold in meters for partitioning records into gps and cellular traces (e.g., 100 meters)|
|dur_constr | temporal constraint in seconds to define a stay (e.g., 300 seconds)|
|spat_constr_gps | spatial constraint in Km to define a gps stay (e.g., 0.2 Km)|
|spat_constr_cell | spatial constraint in Km to define a cellular stay (e.g., 1.0 Km)|

- Output: a csv output file, under folder "processed". The file contains the 5000 users with each user's stays identified for every day.  

How to run it:  
`python main.py "E:/data" "sorted_00.csv" "processed_00.csv" 1000 100 300 0.2 1.0`  

The arguments here are:  
`"E:/data"` gives the work directory, where the input data folder "sorted" and processed data folder are ("processed" folder will be created by the program).  
`"sorted_00.csv"` gives an input data file (one of the file resulting from the preprocessing) for processing. The program will find it under folder "sorted" by searching the input work directory.  
`"processed_00.csv"` specifies the file where to write after the data of each user is processed. The file will be under folder "processed". The folder will be created by the program if it does not exist.  
`1000` sets batch size as 1000, meaning that we allow the program to read 1000 users into memory for one round of processing. Set the number depending on your PC memory size: if your computer has a large memory, set it a large number. You may need some trials and errors. With a 32GB computer, I set it as 5000 users, each of which has two-month observations.   
`100` uses 100 meters as the threshold for partitioning records into gps and cellular traces.  
`300` uses 300 seconds as the temporal constraint to define a stay.  
`0.2` uses 0.2 Km as the spatial constraint to define a gps stay.  
`1.0` uses 1.0 Km as the spatial constraint to define a cellular stay.  

After this step, your data directory looks like the one below. Notice that a new folder "processed" is created and it includes multiple csv files. Each processed data file contains the same set of users as these in the input file. Therefore, one file has 5000 users in our example (depending on how you cut the raw data, this number may be different). Each file in folder "processed" corresponds to one file in folder "sorted" (e.g., "processed_00.csv" contains processed observations of users in sorted_00.csv).  

> **Code block 4.** The data directory after the three preprocessing steps.
```bash
+-- data
¦   +-- raw
¦   ¦   +-- 2019110100
¦   ¦   ¦   +-- part-00000-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- part-00001-96e7044e-3c10-4b04-94d9-be8eaa57f2b1-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- 2019110200
¦   ¦   ¦   +-- part-00000-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- part-00001-b821e85f-6642-4ef2-b0da-64631ddec6a4-c000.csv.gz
¦   ¦   ¦   +-- ...
¦   ¦   +-- ...
¦   +-- unzipped
¦   ¦   +-- 20191101.csv
¦   ¦   +-- 20191101.csv
¦   ¦   +-- ...
¦   +-- sorted
¦   ¦   +-- sorted_00.csv
¦   ¦   +-- sorted_01.csv
¦   ¦   +-- ...
¦   +-- processed
¦   ¦   +-- processed_00.csv
¦   ¦   +-- processed_01.csv
¦   ¦   +-- ...
+-- usernamelist.csv
```

The number of records after processing will be different as well as the variables contained in the input file and the output file. Each processed record in an output csv file could represent one of the two: 1) either a transient point, which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a stay (with positive stay_dur). Each record has 12 fields, including several fields that are copies of the original data and additional fields providing stay information (if the record is a stay) such as latitude, longitude, duration, uncertainty radius.

Table 5 shows a sample of (synthetic) processed data in a csv file. Each record and its 12 fields are described in Table 6. 

**Table 5. Data sample of processed data**

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

**Table 6.** Description of each field in processed data

| <div style="width:100px">Data field</div> | Description                           |
| --------------------------------------- | ------------------------------------- |
|Unix_start_t | The first timestamp when this stay is observed; if this record is a passingby record, it gives the timestamp of this passingby record.  |
|ID | User ID |
|ID_type | OS type of devices in original data; if the record is cellular stay, it is modified as “addedphonestay” (this gives you a chance to count how many stays are cellular stays later) |
|Orig_lat / Orig_long / Orig_unc | Latitude / Longitude / Location uncertainty (in meters), in original data |
|Stay_lat / Stay_long / Stay_unc / Stay_dur |  Latitude / Longitude / uncertainty(meters) / duration(seconds) of identified stay; if not a stay but a passing point, marked as “-1”|
|Stay_label | A label is given to each stay. The label is unique for a stay location belonging to one user in the entire study period. There is no order when labeling the locations (just label a location with 0 when it is first seen).|
|Human_start_t | Translation of unix_start_t; for reading and later calculation convenience; 200507133025 means 2020/05/07 13:30:25 PM.|

    
The remaining python files are called by main.py. So you do not need to work on them. In the following, we introduce functions coded in these files for your interest. You may skip this part. 

#### [gps_traces_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/gps_traces_clustering.py "gps_traces_clustering.py")
The file specifies the function `clusterGPS` called by main.py. The function is to cluster gps data of one user into stays or identifying it as a transient point. 
- Input of the function: gps records of one user ID. The data is structured in a python dictionary containing records of all days. The key of the dictionary gives a date and the value is a list of raw gps records (with Accuracy/uncertainty radius <= 100meters) on the date. A raw record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: gps processed records (either a stay or a transient point) of the input user ID. The data structure is the same as the input: a python dictionary containing records of all days with the key of the dictionary being a date and its value being a list of processed records on the date. There are more fields (12 fields) than the input, so that the identified stay locations are included. Records and fields of a record have the same meanings as these in Table 6 above.  

#### [cellular_traces_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/cellular_traces_clustering.py "cellular_traces_clustering.py")
The file specifies the function clusterPhone called by main.py. The function is to cluster cellular data of one user. 
- Input of the function: cellular records of one user ID. The data is structured in a dictionary containing records of all days for one user. The key of the dictionary gives a date and the value is a list of raw cellular records (with Accuracy/uncertainty radius > 100meters) on the date. A raw cellular record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: processed cellular records of the input user ID. The data structure is the same as the input: a python dictionary containing records of all days with a key being a date and its value being a list of processed cellular records on the date. There are more fields (12 fields) than the input, including the fields of the identified stay location. Records and fields of a record have the same meanings as these in Table 6 above.  

#### [combine_stays_phone_gps.py](https://github.com/feilongwang92/app-data/blob/master/processing/combine_stays_phone_gps.py "combine_stays_phone_gps.py")
The file specifies the function combineGPSandPhoneStops called by `main.py`. The function is to combine processed gps records and processed cellular data of one user. 
- Input of the function: processed gps records (output of function clusterGPS ) and processed cellular data (output of function clusterPhone) of one user ID. 
- Output of the function: processed records of the input user ID. As the same as the input data, the output data is structured in a python dictionary. A key gives a date and its value gives a list of integrated, processed records on the date. The 12 columns of the output have the same meaning as these in Table 6. Each record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a stay (with positive stay_dur). Here, a stay could come from a cellular stay or a gps stay. 

The following python functions are called into the previous three files, i.e., `gps_traces_clustering.py`, `cellular_traces_clustering.py`, and  `combine_stays_phone_gps.py`.

#### [incremental_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/incremental_clustering.py "incremental_clustering.py")

The file specifies the function `cluster_incremental` that is called by `cellular_traces_clustering.py`, `gps_traces_clustering.py` and `combine_stays_phone_gps.py`. 
The function can cluster a list of locations together. It is used when one needs to cluster raw records or identified stays on multiple days based on a specified spatial threshold, so that common stays (e.g., home location) can be identified.
- Input of the function: raw or processed records of one user ID. The data is structured in a python dictionary containing records of all days for a user. The date and the records on the date are a key and its value of the dictionary, respectively.
- Output of the function: processed records of the input user ID. The data structure is the same as the input. As the same as the input data, the output data is structured in a python dictionary. A key gives a date and its value gives a list of integrated, clustered records on the date. There are 11 columns of the output and explanations can be found in “data dictionary for trip_identified by feilong.pdf”. Each record is either a transient point or a stay.

#### [trace_segmentation_clustering.py](https://github.com/feilongwang92/app-data/blob/master/processing/trace_segmentation_clustering.py "trace_segmentation_clustering.py")

The file specifies the function `cluster_traceSegmentation` called by `gps_traces_clustering.py`. The function clusters gps locations belong to one user together. It is used when one needs to cluster raw gps records to identify gps stays on multiple days based on a specified temporal and spatial threshold.
- Input of the function: gps records of one user ID. The data is structured in a python dictionary containing records of all days. The key of the dictionary gives a date and the value is a list of raw gps records (with Accuracy/uncertainty radius <= 100meters) on the date. A raw record includes 7 fields, including Timestamp, ID, ID Type, Latitude, Longitude, Accuracy, Human Time.
- Output of the function: processed records (either a stay or a transient point) of the input user ID. Different from the function clusterGPS, stays identified on different days are distinct and thus need one more step as in clusterGPS to identify common stays. Similarly, the output data structure is the same as the input: a python dictionary containing records of all days with the key of the dictionary being a date and its value being a list of processed records on the date. There are more fields than the input (12 fields in total), as the information of the identified stay locations are included. Each processed record in the output file could represent one of the two: 1) either a transient point which is the same as a record in the original raw input file (with stay_dur = -1); 2) or a gps stay (with positive stay_dur).  See Table 6 for the description of each field of a record. 

#### [class_cluster.py](https://github.com/feilongwang92/app-data/blob/master/processing/class_cluster.py "class_cluster.py")

The file specifies the function `cluster` that defines a python class. The function is called in all clustering algorithms. 
- Input of the function: no input. 
- Output of the function: a python class. Attributes of the class: 1) pList, storing a list of locations (in latitude and longitude) belonging to a cluster; 2) center, storing the center of the cluster in latitude and longitude; 3) radius, the center of the cluster in meters. Methods of the class: 1) `addPoint` is to add a location in latitude and longitude to pList; 2) `updateCenter` is to update center; 3) `distance_C_point` is to compute the Euclidean distance between a location (the input of this function) to the center of the cluster; 4) `radiusC` is to compute radius of the cluster.

#### [oscillation_type1.py](https://github.com/feilongwang92/app-data/blob/master/processing/oscillation_type1.py "oscillation_type1.py")

The file specifies the function `oscillation_h1_oscill` called by `cellular_traces_clustering.py` and `combine_stays_phone_gps.py`. The function is to address oscillation traces in one user's trajectory. 
- Input of the function: processed records for one user ID. The data is structured in a python dictionary containing records of all days for a user. The date and records on the date are the keys and values of the dictionary, respectively. As noted above, each record is either a transient point or a stay.
- Output of the function: processed records for one user ID with oscillation traces being removed. The data structure is the same as the input. 

#### [distace.py](https://github.com/feilongwang92/app-data/blob/master/processing/distance.py "distace.py")

The file specifies the function `distance`. The function is to compute the distance between two locations and is commonly used in almost every py files. 
- Input of the function: a list of two locations in longitude and latitude.
- Output of the function: a float-type number that represents the Euclidean distance (in kilometers) between the input two locations. 
- A note following a previous discussion: The function computes "geodesic distance". The function should not be replaced by a simple Euclidean distance function, as latitude and longitude are not equivalent. Specifically, in the Seattle area, the geodesic distance will increase by about 100 meters if the latitude increases by 0.001, but the geodesic distance will increase by only about 20 meters if the longitude increases by 0.001. And this difference between latitude and longitude should be unique in different areas of the Earth. 

#### [util_func.py](https://github.com/feilongwang92/app-data/blob/master/processing/util_func.py "util_func.py")

The file intends to pack simple functions that are frequently used in processing the data, including  `update_duration` (update stay duration whenever records are modified). 
- Input of update_duration: records of the input user ID. 
- Output of update_duration: records of the input user ID with stay duration updated. 

A test dataset is included in this folder and is organized in folder “test_data”. 
For testing purposes, both the input (example raw data) and output data (processed data) are included. The output data can be compared with your output to identify potential issues in your implementation. 
The test data is in file “anExample”. It contains one user ID and two manually created trajectories on two days, one having 3 trips and the other one having 2 trips. You could find some visualizations of this example data in another document named “workflow of data processing.doc”.


## Codes in Postprocessing Folder
This folder serves examples of how to read in the processed data for postprocessing computations, such as inferring home and work locations. 

### [home_work.py](https://github.com/feilongwang92/app-data/blob/master/postprocessing/home_work.py "home_work.py")

- Input: 1) one of the csv files obtained from the processing folder "processed". Recall that such a csv file contains processed observations of 5000 users; 2) batch size: how many users to read into memory in one round of computation.

- Output: There will be two csv files generated under your work directory. One is "home_inferred.csv" containing home locations and the other is "workplace_inferred.csv" containing work locations. Each row of the home/work file gives the ID and the home/work location of one user, in the form of longitude and latitude.  

How to run it:    
`python home_work.py "E:/data/processed/processed_00.csv" 1000`    
Here, `"E:/data/processed/processed_00.csv"` gives a file containing a part of processed data. The file is under directory `"E:/data/processed/"`. To compute all files under directory `"E:/data/processed/"`, you can write a loop for this command.    
`1000` gives the batch size, meaning that we want to read 1000 users into memory for each round of computation to avoid memory overflow (you can set a different number depending on the memory size).    

    
## Notes of running and understanding the codes

**Notes of preprocessing raw data**

- There may be some unexpected records in the raw data: a few raw records have '\N' value in their “accuracy” field; 

- Duplicated records can be one of two cases: 1) two records are the same for all fields; 2) two records have the same timestamp, latitude and longitude coordinates, but have different location accuracy. 

- A note of loading data to database, if you use a database instead of operating on csv files directly: accuracy of some records could be as large as 562119 meters (should be outliers; be careful when loading data into a database, as in a database, an integer 562119 is loaded as 32768 using a SmallInt datatype). 

- Longitude/latitude in a few raw records have no decimal place (e.g., 45	-125); be careful when you deal with decimal places. These records are removed in the preprocessing steps, as they literally do not give a mobile device's location.

- Some records have a time zone that is different from your study area. For example, the Puget Sound region data have records that are not at Pacific Standard Time. Specifically, for these records, values at time-zone field (the last column) can be -36000, which stands for Alaska time (2 hours later than PST). (Such unexpected records are loaded as -32768 in a database if SmallInt is used.)

**Tips for Addressing "out of memory" issue:**

- If your machine gets a small memory, you can process observations belongs to a small batch of IDs: Read 5000 unique IDs (or 1000 IDs), get observations of these IDs from disk to memory, conduct computations, save results on disk, release memory and read next 5000 IDs. You may find that "sorted" and "processed" data have been cut into files, each of which contains 5000 IDs. This allows you to read in and process data files one by one and avoids memory overflow. 

- Does using a database improve processing speed compared with working on csv files directly? Based on my experiments, using a database may not be a good idea in our cases. Time-saving from using a database is limited as it takes much time for just loading all files into a database table and indexing the table, although it is relatively fast to fetch observations belonging to one ID after the data is loaded. The use of databases has its advantages when we need some frequent data manipulations, for example, when we need to frequently identify and mute one specific ID. For sorting and processing all observations, the use of the database has no clear advantage as the data are processed in batches. 

**Notes for processing data (e.g., identification of trip ends)**

- Most of IDs can be processed quickly, but some “outlier” IDs, who have a large number of records (see an example below), require long computation time. In the worst case, it takes about one day to process such outlier IDs. You may find that one ID has 77,178 records: `f8afa76b6aaaa5cd0c07171f96a2caf9d29911018b44a149d02df1ac910ef4f8` in the file `part201805.csv` in PSRC data from Jan to March of 2018. 

- Tips of addressing “outliers”: when applying multi-processing, sort your IDs into a queue in the reverse order according to the number of observations of the IDs. In this way, the ID with the most number of observations is put at the top of the queue and is processed first.  Use the function pool.apply_async instead of pool.map in Python (see python document for the differences between the two). 

- Codes of some functions seem necessarily complicated. They are coded to save calculation time. For example, originally, it takes a few lines in function diameterExceedCnstr, which is to find out whether the diameter of a cluster (defined as the longest distance between any two locations in the cluster) exceeds 200 meters. For saving computation time, the function is rewritten by applying some additional heuristic rules (see comments in function diameter). 

- For more understandings of the algorithms underlying these codes: Refer to a report [Promises of transportation big data, 2019](https://www.fhwa.dot.gov/planning/tmip/publications/other_reports/data_emerging_tech/index.cfm "Promises of transportation big data, 2019") that is a deliverable of the FHWA project in 2018. Refer to the paper by [Wang et al., extracting trip ends from multi-sourced data, 2019.](http://www.sciencedirect.com/science/article/pii/S0968090X18316085 "Wang et al., extracting trip ends from multi-sourced data, 2019.") 

**Deploy computation environment**

- Codes are written in **python 2.7**; do remember that python codes are sensitive to package versions. The codes are tested in an environment of **anaconda2-4.2.0**. So the easiest way of duplicating the computation environment is to install [anaconda2-4.2.0](https://repo.anaconda.com/archive/ "anaconda2-4.2.0"). Note, it is not the latest anaconda version. It is found that the outputs could be different if an environment other than anaconda2-4 is used; it is not clear which package dependency raises this issue.
