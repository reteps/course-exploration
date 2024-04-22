'''
Year Published,Unit Code,Unit Name,Item,,2023-2024,2022-2023,2021-2022,2020-2021,2019-2020,2018-2019,2017-2018,2016-2017,2015-2016,2014-2015,2011 Target,2013 Target
FY2024,1B1-KL-KL0-306,ACES courses,9500,ICES Teaching Evaluations,,,,,,,,,,,,
FY2024,1B1-KL-KL0-306,ACES courses,9520,% Sections using ICES,,54.5,43.6,46.3,,,,,,,,
FY2024,1B1-KL-KL0-306,ACES courses,9540,Faculty ICES ratings,,,,,,,,,,,,
FY2024,1B1-KL-KL0-306,ACES courses,9560,Top 10% Faculty,,12,12,0,,,,,,,,
FY2024,1B1-KL-KL0-306,ACES courses,9580,Next 20% Faculty,,0,12,15,,,,,,,,
FY2024,1B1-KL-KL0-306,ACES courses,9600,Middle 40% Faculty,,35,53,38,,,,,,,,
FY2024,1B1-KL-KL0-306,ACES courses,9620,Next 20% Faculty,,41,18,31,,,,,,,,
FY2024,1B1-KL-KL0-306,ACES courses,9640,Bottom 10% Faculty,,12,6,15,,,,,,,,


[
    "ACES courses": {
        "Top 10% Faculty": {
            "2023-2024": 12,
            "2022-2023": 12,
        },
        "Next 20% Faculty": {
            "2023-2024": 0,
            "2022-2023": 12,
        },   
    }
}
'''

import csv
import json

data = {}
with open("ices-headcount.csv", 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)[6:-2]  # Include all years after current year
    for row in reader:
        unit_code = row[1]
        unit_name = row[2]
        item_name = row[4]
        if "9620" == row[3]:
            item_name =  r"Middle Bottom 20% Faculty"
        if unit_name not in data:
            data[unit_name] = {}
        count = 0
        if item_name:  # Check if item_name is not empty
            data[unit_name][item_name] = {headers[i]: float(row[6+i]) if '.' in row[6+i] else (int(row[6+i]) if row[6+i] != '' else None) for i in range(len(headers))}  # Include data for all years
        if not any(map(lambda x: x != None, data[unit_name][item_name].values())):
            del data[unit_name][item_name]
        # Exclude Generalizations
        if 'XXX' in unit_code:
            del data[unit_name]

# Remove empty units
data = {unit_name: data[unit_name] for unit_name in data if data[unit_name]}

# Remove units with just 'Headcount' rows
new_data = {}
for unit_name in data:
    keep = False
    for item_name in data[unit_name]:
        if 'Headcount' not in item_name:
            keep = True
            break
    if keep:
        new_data[unit_name] = data[unit_name]
data = new_data
# # Restructure the data 
# restructured = {}
for unit_name in data:
    data[unit_name]["years"] = list(data[unit_name][list(data[unit_name].keys())[0]].keys())
    num_years = len(data[unit_name]["years"])
    for item_name in data[unit_name]:
        if item_name == "years":
            continue
        data[unit_name][item_name] = list(data[unit_name][item_name].values()) # + [None] * (num_years - len(data[unit_name][item_name]))

with open('ices-headcount.json', 'w') as f:
    json.dump(data, f, indent=4)
