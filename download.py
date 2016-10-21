#!/usr/bin/env python

#--------------------------------------------------------------------------------

# TODO:
#    2. Figure out what writelines() pukes.
#    3. Put results in directory
#    4. Dynamically create directory structure based on chapter names.
#    5. Store URL for each problem description with (in?) problem description.
#    6. Better logging.
#    7. Makefile to convert markdown to other formats.
#    8. virtualenv with requirements.txt

# TODONE:
#    1. Fix FIXMEs.

#--------------------------------------------------------------------------------

import requests
import json
import html2text

#--------------------------------------------------------------------------------

base_url = "https://www.hackerrank.com/rest/contests/master"

#--------------------------------------------------------------------------------

def get_chapters_in_track(track):
    '''Get a dictionary of chapters for a given track'''
    # https://www.hackerrank.com/rest/contests/master/tracks/python/chapters/
    url = base_url + "/tracks/" + track + "/chapters"
    response = requests.get(url)
    data =response.json()
    chapters = data['models']
    return chapters

#--------------------------------------------------------------------------------

def get_challenges_in_chapter(track, slug):
    '''Get a dictionary of challenges in a chapter'''
    # "https://www.hackerrank.com/rest/contests/master/categories/python|py-introduction/challenges"
    url = base_url + "/categories/" + track + "|" + slug + "/challenges" 
    response = requests.get(url)
    data = response.json()
    challenges = data['models']
    return challenges

#--------------------------------------------------------------------------------

def get_challenge_body(slug):
    '''Get body (problem description) for a given challenge'''
    # "https://www.hackerrank.com/rest/contests/master/challenges/py-hello-world" 
    url = base_url + "/challenges/" + slug
    response = requests.get(url);
    data = response.json() 
    html = data['model']['body_html']
    name = data['model']['name']
    preview = data['model']['preview']

    parser = html2text.HTML2Text()

    parser.single_line_break = True
    parser.ignore_links = True
    parser.wrap_links = False
    parser.mark_code = True

    try:
        md = parser.handle(html)
    except:
        print "%s: %s" % (slug, "Puke! Vomit!")

    with open(name + ".md", 'w') as fd:
        fd.write("# %s\n\n" % name)
        fd.write("%s\n\n" % preview)
        try:
            fd.writelines(md)
        except:
            print "%s: %s" % (slug, "Puke! Vomit!")

#--------------------------------------------------------------------------------

def main():
    track = "python"
    chapters = get_chapters_in_track("python")
    for chapter in chapters:
        slug = chapter['slug']
        print "[ %s ]----------------------------------------" % (slug)
        challenges = get_challenges_in_chapter(track,slug)        
        for challenge in challenges:
            slug = challenge['slug']
            print "    %s" % (slug)
            get_challenge_body(slug)
        print

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#--------------------------------------------------------------------------------
