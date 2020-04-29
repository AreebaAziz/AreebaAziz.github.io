'''
python generator.py <filename>
'''

import sys
import re

SECTIONS = "sections"

try:
    filename = sys.argv[1]
except IndexError:
    print("ERROR: Need filename argument.")
    exit(1)

print("Filename: " + filename)

file = open(filename)

week = -1
try:
    week = file.readline().strip().replace("%% Week ", "")
except Exception as e:
    print("ERROR: first line of text file must be '%% Week <int>'")
    raise e

print("Week: " + week)

text = file.read().strip()
file.close()

sections = re.findall("%% ?begin ?(\[[^\]]*][^%]*)%% ?end", text, re.DOTALL)

for si in range(len(sections)):
    tags = re.findall("\[(.*)\]", sections[si])
    tags = [s.strip() for s in tags[0].split(",")]
    sec_filename = SECTIONS + "/w-{week}-s-{seci:02d}".format(week=week,seci=si)
    # create the section file
    text = re.findall("\[.*\](.*)", sections[si], re.DOTALL)[0].strip()
    if text != "": 
        file = open(sec_filename, "w")
        file.write(text)
        file.close()
