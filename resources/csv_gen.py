# I would need the Name, Present Days, Total Days, Present %,
# Eligible for Certification(if >= 80% present)
 # att = 40 *100 / count_totaldays()

import os
import csv
import collections


pathName = os.getcwd()
fileName = os.listdir(pathName)

name_list = list()


rows = 0
for root, dirs, files in os.walk(pathName):
    for file in files:
        if file.endswith(".csv"):
            with open(file, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                rows += len(list(csv_reader))


def count_presentdays(name, line):
    # for line in csv_reader:
    if line[4] == 'Present':
        name_list.append(line[2])
    present_days = collections.Counter(name_list)
    return present_days.get(name)


with open('new_csv.csv', 'w') as csvfile:
        filewriter = csv.writer(
            csvfile, delimiter=',')
        filewriter.writerow([
            'Name', 'Present_days',
            'Total_days',
        ])
        for root, dirs, files in os.walk(pathName):
            for file in files:
                if file.endswith(".csv"):
                    with open(file, 'r') as csv_file:
                        csv_reader = csv.reader(csv_file)
                        next(csv_file)
                        for line in csv_reader:
                            filewriter.writerow([line[2], count_presentdays(line[2], line), rows])
