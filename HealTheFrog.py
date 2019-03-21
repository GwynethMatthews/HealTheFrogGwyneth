# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 18:07:13 2019

@author: Gwyneth Matthews
"""

import csv
import operator as op
import itertools
import re
import datetime
import json 

# open patient information file
with open('patients.json') as json_file:  
    patient_information = json.load(json_file)

# setting up new dictionary to save data 
all_data = {}
all_data["patients"] = []

# open test codes and labels file and convert to reader
with open('labresults-codes.csv', 'r') as labresults_codes:
    reader1 = csv.reader(labresults_codes)
    
    fields_lab_codes = [] 
    test_codes = [] 
    
    fields_lab_codes = next(reader1) 

    for row in reader1:
        test_codes.append(row)

# open lab results file and convert to reader
with open('labresults.csv', 'r') as labresults:

    reader2 = csv.reader(labresults)
    
    fields_lab_results = [] 
    lab_results = [] 
    
    fields_lab_results = next(reader2) 

    for row in reader2:
        lab_results.append(row) 

# sort and group based on patient hospital id
lab_results.sort(key = op.itemgetter(0))
group_by_hospital_id = itertools.groupby(lab_results, key = op.itemgetter(0))

# seperate lab results for different patients
patients_lab_results= []
identifiers = []

for hospital_id, tests in group_by_hospital_id:
    
    patients_lab_results.append(list(tests))      
    identifiers.append(hospital_id)

# seperate each patient's results by profile
for patient in range(len(identifiers)):
    patient_tests = patients_lab_results[patient]
    
    # sort and group based on test profile
    patient_tests.sort(key = op.itemgetter(3))
    group_by_profile = itertools.groupby(patient_tests, key = op.itemgetter(3))
    
    # create list for patient's lab results
    lab_results = []
    
    # seperate a patients lab results for different profiles

    profile_results = []
    
    for profile_label, results in group_by_profile:
        
        profile_results.append(list(results))      
        
    for profile in profile_results:
        # converting timestamp to correct format
        d = datetime.datetime.strptime(profile[0][2], '%d/%m/%Y')
        timestamp = d.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # collect profile data (name and code)
        profile_data = {}
        profile_data["name"] = profile[0][3]
        profile_data["code"] = profile[0][4]
        
        # combine panel results
        panel = []
        
        for test in profile:
            # organise test results and put in correct format
            test_in_panel = {}
            
            for key in test_codes:
                # get test code and label from test_codes
                if key[0] == test[-4]:
                    test_in_panel["code"] = key[1]
                    test_in_panel["label"] = key[2]
                    
                    # seperate results from different tests
                    test_name = str(None) # dummy variable to be over written
                    j = 0 # variable for cycling through results
                    
                    while test_name != key[0] and j < 25:
                        # result into test code and value
                        test_name, res = test[j + 5].split('~')
                        j += 1
                    
                    test_in_panel["value"] = res
                    test_in_panel["unit"] = test[-3]
                    
                    # collect lower and upper ranges
                    lower = re.search(r'\d+$',test[-2]) # detects a number else gives None
                    upper = re.search(r'\d+$',test[-1])
                    
                    if lower == None:
                        lower = ''
                    else:
                        lower = float(lower.group())
                        
                    if upper == None:
                        upper = ''
                    else:
                        upper = float(upper.group())
                        
                    test_in_panel["lower"] = lower
                    test_in_panel["upper"] = upper
            
            # combine panel test results        
            panel.append(test_in_panel)
        
        # combine timestamp, profile information and panel results
        patient_profile_lab_results = {}
        patient_profile_lab_results["timestamp"] = timestamp
        patient_profile_lab_results["profile"] = profile_data
        patient_profile_lab_results["panel"] = panel
        
        # add profile results to lab results of patient
        lab_results.append(patient_profile_lab_results)
    
    # add all patients data to the main data file     
    for patient_details in patient_information: # patient information is the file with id, first name, last name, dob
        # copy so original isn't altered
        data_to_add = patient_details.copy()
        
        # add lab results to correct patient's records
        if data_to_add["identifiers"] == [str(identifiers[patient])]:
            # remove identifier
            del data_to_add['identifiers']
            
            # add lab results
            data_to_add["lab_results"] = lab_results
                       
            # add patient to main data file
            all_data["patients"].extend([data_to_add])

# save output file in json format
with open('output.json', 'w') as outfile:
    json.dump(all_data, outfile, ensure_ascii=False)


        
    
