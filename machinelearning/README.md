# Machine Learning Pipeline

The machine learning pipeline consist of:
```mermaid
graph LR
  A(events from detector) --> B(data preparation <br/>& feature engineering)
  B --> C(model development <br/>& training)
  C --> D(model evaluation)
  D --> E(prediction)
```

## Input format

CSV file with the following columns:
- timestamp when the event is generated
- PID of the process
- type of event (0=open, 1=create, 2=delete, 3=encrypt)
- severity of the event seen from BPF (according to threshold crossed and pattern matches)
- ID of any pattern matched by BPF
- for each event type
  - wether the number of events of that type crossed a threshold (note we can also count without relying on BPF)
- name of the file or name of the encryption function

## Data preparation & feature engineering

The inputs from the detector consist of file open, create, delete and encypt events.
These events are stored in a CSV file.

Based on these events the following features can be calculated and normalised:

- for each type of event (open, create, delete, encrypt)
  - average number of events per minute (may be this is too long?)
  - maximum number of events per minute 

- for each possible sequence of event
  - average number of matches per minute
  - maximum number of macthes per minute 

- possible sequences to consider
  - Open, Create, Delete
  - Open, Create, Encrypt, Delete
  - Open, Create, Encrypt ... Encrypt, Delete (variable number of Encrypts in the middle)
  - Delete, Delete, Delete (erasing lots of files in sequence)
  - Open ... Open, Create ... Create, Encrypt ... Encrypt, Delete ... Delete (operations done in batch/parallel)

- type of files accessed
  - sensitive linux files like /etc/*, /var/*, /usr/*, /sys/*
  - especially if these files are modified or created


Prepare the data:
```shell
./dataprep.py
```

Sample output:
```rb
       C_max  C_sum  D_max  D_sum  E_max  E_sum  O_max  O_sum  P_max  P_sum   CDO  COC  COO   DOC  DOO   EEE   OCD  OCO  OOC  OOO
PID
1          0      0      0      0      0      0      4      5      0      0     0    0    0     0    0     0     0    0    0    3
221        0      0      0      0      0      0     20     20      0      0     0    0    0     0    0     0     0    0    0   18
626        0      0      0      0      0      0     16     16      0      0     0    0    0     0    0     0     0    0    0   14
714        0      0      0      0      0      0     12     12      0      0     0    0    0     0    0     0     0    0    0   10
838        0      0      0      0      0      0      3      9      0      0     0    0    0     0    0     0     0    0    0    7
1019       0      0      0      0     36   1501      0      0      0      0     0    0    0     0    0  1499     0    0    0    0
1195       0      0      0      0      0      0     11     11      0      0     0    0    0     0    0     0     0    0    0    9
1196       0      0      0      0      0      0      7      7      0      0     0    0    0     0    0     0     0    0    0    5
1197       0      0      0      0      0      0     10     10      0      0     0    0    0     0    0     0     0    0    0    8
1202       0      0      0      0      0      0      8      8      0      0     0    0    0     0    0     0     0    0    0    6
1230       0      0      0      0      0      0      1     60      0      0     0    0    0     0    0     0     0    0    0   58
1237       0      0      0      0      0      0      1     36      0      0     0    0    0     0    0     0     0    0    0   34
1238       0      0      0      0      0      0      1     27      0      0     0    0    0     0    0     0     0    0    0   25
1239       0      0      0      0      0      0      1     38      0      0     0    0    0     0    0     0     0    0    0   36
1240       0      0      0      0      0      0      1     30      0      0     0    0    0     0    0     0     0    0    0   28
1555       0      0      0      0    207   1978      0      0      0      0     0    0    0     0    0  1976     0    0    0    0
29952      0      0      0      0     63    326      0      0      0      0     0    0    0     0    0   324     0    0    0    0
30490     17   1690     17   1691      0      0     20   1750     17   1690  1689    0    0  1635   55     0  1690    0   55    5
30493      0      0      0      0      0      0     12     19      0      0     0    0    0     0    0     0     0    0    0   17
30495    233   1216     17    983      0      0    278   1458     17    983   983  228    5   949   34     0   983  233   39  201
30496      0      0      0      0      0      0      3      3      0      0     0    0    0     0    0     0     0    0    0    1
```

## Model development

For supervised learning (SVM) we need to "label" each data sample from above with 1 "malware" or 0 "not malware".

Train the model and show predictions:
```shell
./model.py --mode train
```

Sample output:
```rb
Score: 1.000000
      PID  C_max  C_sum  D_max  D_sum  E_max  E_sum  O_max  O_sum  P_max  P_sum   CDO  COC  COO   DOC  DOO   EEE   OCD  OCO  OOC  OOO  PREDICTION
0       1      0      0      0      0      0      0      4      5      0      0     0    0    0     0    0     0     0    0    0    3           0
1     221      0      0      0      0      0      0     20     20      0      0     0    0    0     0    0     0     0    0    0   18           0
2     626      0      0      0      0      0      0     16     16      0      0     0    0    0     0    0     0     0    0    0   14           0
3     714      0      0      0      0      0      0     12     12      0      0     0    0    0     0    0     0     0    0    0   10           0
4     838      0      0      0      0      0      0      3      9      0      0     0    0    0     0    0     0     0    0    0    7           0
5    1019      0      0      0      0     36   1501      0      0      0      0     0    0    0     0    0  1499     0    0    0    0           0
6    1195      0      0      0      0      0      0     11     11      0      0     0    0    0     0    0     0     0    0    0    9           0
7    1196      0      0      0      0      0      0      7      7      0      0     0    0    0     0    0     0     0    0    0    5           0
8    1197      0      0      0      0      0      0     10     10      0      0     0    0    0     0    0     0     0    0    0    8           0
9    1202      0      0      0      0      0      0      8      8      0      0     0    0    0     0    0     0     0    0    0    6           0
10   1230      0      0      0      0      0      0      1     60      0      0     0    0    0     0    0     0     0    0    0   58           0
11   1237      0      0      0      0      0      0      1     36      0      0     0    0    0     0    0     0     0    0    0   34           0
12   1238      0      0      0      0      0      0      1     27      0      0     0    0    0     0    0     0     0    0    0   25           0
13   1239      0      0      0      0      0      0      1     38      0      0     0    0    0     0    0     0     0    0    0   36           0
14   1240      0      0      0      0      0      0      1     30      0      0     0    0    0     0    0     0     0    0    0   28           0
15   1555      0      0      0      0    207   1978      0      0      0      0     0    0    0     0    0  1976     0    0    0    0           0
16  29952      0      0      0      0     63    326      0      0      0      0     0    0    0     0    0   324     0    0    0    0           0
17  30490     17   1690     17   1691      0      0     20   1750     17   1690  1689    0    0  1635   55     0  1690    0   55    5           1
18  30493      0      0      0      0      0      0     12     19      0      0     0    0    0     0    0     0     0    0    0   17           0
19  30495    233   1216     17    983      0      0    278   1458     17    983   983  228    5   949   34     0   983  233   39  201           1
20  30496      0      0      0      0      0      0      3      3      0      0     0    0    0     0    0     0     0    0    0    1           0
```
