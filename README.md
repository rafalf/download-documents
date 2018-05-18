### Install:
* [Python 3](https://www.python.org/downloads/release/python-363/)
* start command prompt as Administrator, go to download-documents e.g. ```CD path_download-documents```  and run this command: ```pip install -r requirement.txt```

### Config:
* rename ```config.sample.yaml``` to ```config.yaml``` and add user and password.

### Run:
* start command prompt as Administrator and type in: ```CD PATH_TO_FOLDER``` e.g. ```CD D:\download-documents```
* run: ```python run.py```

### Latest chrome driver:
[chromedriver](http://chromedriver.chromium.org/)


### Output:

* output.csv
```
DocName            DocType    FolderName
5661_1.pdf   Inspection Sheet  012740101107
5660_1.pdf          Plot Plan  012740101107
5659_1.pdf  State Application  012740101107
5535_1.pdf   Inspection Sheet  012740101107
5534_1.pdf          Plot Plan  012740101107
```
* files are downloaded and then moved to: ```results\FolderName```


### Input:

* idle - to be processed by the script 
* processed - have been processed by the script
```
TrkNbr,Status
026939025202,idle
012740101107,idle
028742151401,idle
010941133301,idle
028742275301,idle
014206002200,idle
012740021101,idle
002940042202,idle
012740034401,idle
008938205102,idle
002840054103,idle
002940042205,idle
010941331407,idle
010262000101,idle
012740101105,idle
```

### Log file:
* all actions are logged in log.log file


