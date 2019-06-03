#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# CSV Normalization
#
# leeann.bent@gmail.com
#
# This program normalizes (sanitizes) CSV input. It assumes input is in UTF-8
# and non-specified time zones are PT. Invalid characters are replaced with
# Unicode Replacement Character and invalid rows (i.e. - because the Unicode 
# Replacement character makes the data unparseable) are dropped.
#
# Format is:
#    Timestamp Address ZIP FullName FooDuration BarDuration TotalDuration Notes 
#
# Example usage: 
#
#   cat data_file.csv | csv_normalize > data_file_norm.csv
#
# Expected input:
#   4/1/11 11:00:00 AM,"123 4th St, Anywhere, AA",94121,Monkey Alberto,1:23:32,1:32:33,zzsasdfa,I am the very model of a modern major general
# Example output:
#   2011-04-01T14:00:00-04:00,"123 4th St, Anywhere, AA",94121,MONKEY ALBERTO,5012.0,5553.0,10565.0,I am the very model of a modern major general

import csv 
from datetime import datetime, timedelta
import pytz
from pytz import timezone
import sys


def sanitize_unicode(csv_row):
  """Replace invalid Unicode characters with the Unicode Replacement char.

     Input:
       csv_row - List of UTF-8 strings, built from CSV values. The input row.

     Returns:
       csv_row sanitized.
  """
  sanitized_csv_row = []
  for csv_element in csv_row:
    try:
      u_csv_element = csv_element.decode('utf8')
      sanitized_csv_row.append(u_csv_element)
    except UnicodeDecodeError as e:
      clean_element = csv_element[:e.start].decode('utf8') + u'\uFFFD' + csv_element[e.end:].decode('utf8')  
      sanitized_csv_row.append(clean_element)
  return sanitized_csv_row
 

def iso_est_date(pt_date_string):
  """Convert %m/%d/%y %H:%M:%S %p timestamp to ISO EST format.

     Input:
       pt_date_string - Formatted as %m/%d/%y %H:%M:%S %p 

     Returns:
       ISO-8601 EST date string. 
  """
  # Since input is assumed to be Pacific time, use American dates.
  try:
    pt_datetime = datetime.strptime(pt_date_string, "%m/%d/%y %I:%M:%S %p")
    pt_datetime_tz = timezone('US/Pacific').localize(pt_datetime)
  except ValueError as e:
    return None, e
  return pt_datetime_tz.astimezone(timezone('US/Eastern')).isoformat(), None

  
def duration_to_fps(duration_string):
  """Convert HH:MM:SS.MS to floating point seconds.
      
     Input:
       duration_string - String as HH:MM:SS

     Returns:
       Duration as floating point seconds.
  """
  # We can't use datetime because the timespans are longer than 24 hours.
  duration_set = duration_string.split(':')
  duration_set_ms = duration_set[2].split('.')

  # Only some of the items have MS specified.
  if len(duration_set_ms) == 2:
    duration = timedelta(hours=int(duration_set[0]), 
                         minutes=int(duration_set[1]), 
                         seconds=int(duration_set_ms[0]), 
                         milliseconds=int(duration_set_ms[1]))
  else:
    duration = timedelta(hours=int(duration_set[0]),
                         minutes=int(duration_set[1]),
                         seconds=int(duration_set_ms[0]))
  return duration


def utf8_print(u_csv_row):
  """Format string for utf8 printing."""
  s = unicode(','.join(u_csv_row)).encode('utf8')
  sys.stdout.write(s)
  sys.stdout.write("\n")


def maybe_quote(u_csv_element):
  """ If a comman is present in the element, protect it with quotes."""
  if "," in u_csv_element:
    return ("\"" + u_csv_element +"\"")
  else:
    return u_csv_element


def process_csv_input():
  with sys.stdin as csv_input:
    reader = csv.reader(csv_input)
    for csv_row in reader:
      new_row = []

      # Sanitize the row and convert to Unicode first.
      u_csv_row = sanitize_unicode(csv_row) 
        
      # Just skip the header row.
      if u_csv_row[0] == 'Timestamp':
        utf8_print(u_csv_row)
        continue

      # Convert the timestamp.
      # TODO(lbent): Add better error checking on indexing of fields.
      (iso_ts, e) = iso_est_date(u_csv_row[0]) 
      if not iso_ts:
        sys.stderr.write("WARNING: (%s) Dropping row %s\n" % (e, csv_row))
        continue
      new_row.append(iso_ts)

      # Quote the address if it needs it. 
      new_row.append(maybe_quote(u_csv_row[1]))

      # Pad the ZIP code to 5 digits.
      new_row.append("{:0>5}".format(u_csv_row[2]))

      # Make the name upper case.
      new_row.append(u_csv_row[3].upper())

      # Durations 
      first_duration = duration_to_fps(u_csv_row[4])
      new_row.append("%s" % first_duration.total_seconds())
      second_duration = duration_to_fps(u_csv_row[5])
      new_row.append("%s" % second_duration.total_seconds())
      new_row.append("%s" % (first_duration + second_duration).total_seconds())

      # Quote notes if it needs it. 
      new_row.append(maybe_quote(u_csv_row[7]))
      
      # Print the new row.
      utf8_print(new_row)
	

# Let's pretend this is a main
process_csv_input()
