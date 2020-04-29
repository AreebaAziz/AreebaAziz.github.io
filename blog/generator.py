'''
python generator.py <filename>
'''

import sys
import re
import os

SECTIONS = "sections"
TAGS = "tags"
POSTS = "posts"

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
full_content = ""

for si in range(len(sections)):
    tags = re.findall("\[(.*)\]", sections[si])
    tags = [s.strip() for s in tags[0].split(",")]
    sec_filename = SECTIONS + "/w-{week}-s-{seci:02d}".format(week=week,seci=si)
    # create the section file
    text = re.findall("\[.*\](.*)", sections[si], re.DOTALL)[0].strip()
    if text != "": 
        full_content += text

        # write contents into the section file
        file = open(sec_filename, "w")
        file.write(text)
        file.close()

        # create or append to tag files
        for tag in tags:
            file = open(TAGS + "/" + tag, "a")
            file.write(sec_filename.replace(SECTIONS + "/", "") + "\n")
            file.close()

# now write the full contents of the blog post in one file
blog_filename = POSTS + "/w-{week}".format(week=week)

file = open(blog_filename + ".md", "w")
file.write(full_content)
file.close()

# now write it in HTML format
os.system("markdown2 {0}.md > {0}.html".format(blog_filename))