# data-sanitize

This program normalizes (sanitizes) CSV input. It assumes input is in UTF-8
and non-specified time zones are PT. Invalid characters are replaced with
Unicode Replacement Character and invalid rows (i.e. - because the Unicode 
Replacement character makes the data unparseable) are dropped.

Format of the data is expected to be:
   Timestamp Address ZIP FullName FooDuration BarDuration TotalDuration Notes 

## Getting Started

### Prerequisites

This code is written for Python 2.7. It assumes the installation of the 
pytz library, which can be found [here](https://pypi.org/project/pytz/). 

### Running 

```
cat data_file.csv | csv_normalize > data_file_norm.csv
```

Example input:

```
  4/1/11 11:00:00 AM,"123 4th St, Anywhere, AA",94121,Monkey Alberto,1:23:32,1:32:33,zzsasdfa,I am the very model of a modern major general
```

Example output:

```
  2011-04-01T14:00:00-04:00,"123 4th St, Anywhere, AA",94121,MONKEY ALBERTO,5012.0,5553.0,10565.0,I am the very model of a modern major general
```

## Authors

* **Leeann Bent** - *Initial work* - [leeannbent](https://github.com/leeannbent)

