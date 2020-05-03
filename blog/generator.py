'''
python generator.py <filename> [d]
if d is given, then we will do a dry run. 
We'll create the html page, but not any sections or tags, and we won't modify
the index.html page either. 
'''

import sys
import re
import os

SECTIONS = "sections"
TAGS = "tags"
POSTS = "posts"
TEMPLATE_HTML = "template.html"
INDEX_HTML = "../index.html"
BLOG_REPLACEMENT = "<!-- ADD NEW BLOG POSTS HERE -->"

try:
    filename = sys.argv[1]
except IndexError:
    print("ERROR: Need filename argument.")
    exit(1)

try:
    dryrun = sys.argv[2]
except Exception as e:
    dryrun = False
else:
    dryrun = True # accept any string to indicate dryrun

print("Filename: " + filename)

file = open(filename)

week = -1
try:
    week = file.readline().strip().replace("%% Week ", "")
except Exception as e:
    print("ERROR: first line of text file must be '%% Week <int>'")
    raise e

print("Week: " + week)

lines = file.readlines()
file.close()

sections = []

# find the %% begin line
li = 0
section = ""
while li < len(lines):
    while li < len(lines):
        if re.search("%% ?begin", lines[li]) is not None:
            section += lines[li]
            li += 1
            break
        li += 1

    # find the %% end line
    while li < len(lines):
        if re.search("%% ?end", lines[li]) is not None:
            li += 1
            break
        section += lines[li]
        li += 1

    section = re.sub("%% ?begin", "", section)
    section = re.sub("%% ?end", "", section)
    sections.append(section)
    section = ""

full_content = ""
all_tags = []

for si in range(len(sections)):
    tags = re.findall("\[(.*)\]", sections[si])
    text = sections[si].replace(tags[0], '', 1).replace('[','',1).replace(']','',1)
    tags = [s.strip().lower() for s in tags[0].split(",")]

    sec_filename = SECTIONS + "/w-{week}-s-{seci:02d}".format(week=week,seci=si)
    # create the section file
    if text != "": 
        full_content += text

        # write contents into the section file, if not dryrun
        if not dryrun:
            file = open(sec_filename, "w")
            file.write(text)
            file.close()

        # create or append to tag files, if not dryrun
        for tag in tags:
            if tag != '' and tag not in all_tags:
                all_tags.append(tag)
                if not dryrun:
                    file = open(TAGS + "/" + tag, "a")
                    file.write(sec_filename.replace(SECTIONS + "/", "") + "\n")
                    file.close()

# now write the full contents of the blog post in one file
blog_filename = POSTS + "/w-{week}".format(week=week)

file = open(blog_filename + ".md", "w")
file.write(full_content)
file.close()

# find all the main headings
headings = re.findall("[^#]###[^#](.*)", full_content)
headings = [s.strip() for s in headings]

# now write it in HTML format
os.system("markdown2 {0}.md --extras header-ids -x fenced-code-blocks > {0}.html".format(blog_filename))

# read the html generated
file = open(blog_filename + ".html", "r")
html_content = file.read()
file.close()

# read the template html file
file = open(TEMPLATE_HTML, "r")
template = file.read()
file.close()

# replace appropriate blog content in the template
content = template.replace("%%WEEK_NUM%%", "{}/{}/{}".format(week[0:2], week[2:4], week[4:6]))
content = content.replace("%%TAGS%%", ", ".join(all_tags))
content = content.replace("%%CONTENT%%", html_content)
hds = ""
for h in headings:
    hds += "<a href=\"#{headingsm}\" class=\"w3-bar-item w3-button w3-hide-small w3-hover-pink w3-black\"> &nbsp;{heading}</a>".format(heading=h, headingsm=h.lower().replace(" ", "-"))
content = content.replace("%%HEADINGS%%", hds)

# write this content to the html file
file = open(blog_filename + ".html", "w")
file.write(content)
file.close()

# now add this blog post link to the home page (index.html), if not dryrun
if not dryrun:
    file = open(INDEX_HTML, "r")
    orig = file.read()
    file.close()

    new_blog = "{repl}\n<tr>\n<td><a href=\"blog/posts/w-{week}.html\">Week {y}/{m}/{d}</a></td>\n<td>{tags}</td>\n</tr>\n"
    new_blog = new_blog.format(week=week, y=week[0:2], m=week[2:4], d=week[4:6], tags=", ".join(all_tags), repl=BLOG_REPLACEMENT)

    new_index_html = orig.replace(BLOG_REPLACEMENT, new_blog)

    file = open(INDEX_HTML, "w")
    file.write(new_index_html)
    file.close()
