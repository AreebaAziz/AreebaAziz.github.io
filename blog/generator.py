'''
python generator.py <filename>
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
all_tags = []

for si in range(len(sections)):
    tags = re.findall("\[(.*)\]", sections[si])
    text = sections[si].replace(tags[0], '', 1).replace('[','',1).replace(']','',1)
    tags = [s.strip() for s in tags[0].split(",")]

    sec_filename = SECTIONS + "/w-{week}-s-{seci:02d}".format(week=week,seci=si)
    # create the section file
    if text != "": 
        full_content += text

        # write contents into the section file
        file = open(sec_filename, "w")
        file.write(text)
        file.close()

        # create or append to tag files
        for tag in tags:
            if tag != '':
                all_tags.append(tag)
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

# write this content to the html file
file = open(blog_filename + ".html", "w")
file.write(content)
file.close()

# now add this blog post link to the home page (index.html)
file = open(INDEX_HTML, "r")
orig = file.read()
file.close()

new_blog = "{repl}\n<tr>\n<td><a href=\"blog/posts/w-{week}.html\">Week {y}/{m}/{d}</a></td>\n<td>{tags}</td>\n</tr>\n"
new_blog = new_blog.format(week=week, y=week[0:2], m=week[2:4], d=week[4:6], tags=", ".join(all_tags), repl=BLOG_REPLACEMENT)

new_index_html = orig.replace(BLOG_REPLACEMENT, new_blog)

file = open(INDEX_HTML, "w")
file.write(new_index_html)
file.close()
