#!/usr/bin/env python

#--------------------------------------------------------------------------------

# TODO:
#    2. Figure out what writelines() pukes.
#    5. Store URL for each problem description with (in?) problem description.
#    6. Better logging.
#    7. Makefile to convert markdown to other formats.
#    9. Add function(s) to get a list of tracks
#   10. Add support for command line arguments to list/select/download tracks

# TODONE:
#    1. Fix FIXMEs.
#    3. Put results in directory
#    4. Dynamically create directory structure based on chapter names.
#    8. virtualenv with requirements.txt

#--------------------------------------------------------------------------------

import html2text
import json
import os.path
import requests

#--------------------------------------------------------------------------------

base_url = "https://www.hackerrank.com/rest/contests/master"

#--------------------------------------------------------------------------------

def get_tracks():
    '''Get a dictionary of tracks'''
    # https://www.hackerrank.com/rest/contests/master/tracks/
    url = base_url + "/tracks/"
    response = requests.get(url)
    data = response.json()
    tracks = data['models']
    return tracks

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

def get_challenge_data(slug):
    # "https://www.hackerrank.com/rest/contests/master/challenges/py-hello-world" 
    url = base_url + "/challenges/" + slug
    response = requests.get(url);
    data = response.json() 
    return data

#--------------------------------------------------------------------------------

def get_challenge_body(data):
    '''Get body (problem description) for a given challenge'''
    html = data['model']['body_html']

    parser = html2text.HTML2Text()

    parser.single_line_break = True
    parser.ignore_links = True
    parser.wrap_links = False
    parser.mark_code = True

    try:
        md = parser.handle(html)
    except:
        print "%s: %s" % (slug, "Puke! Vomit!")

    return md

#--------------------------------------------------------------------------------

def get_challenge_name(data):
    '''Get name for a given challenge'''
    name = data['model']['name']
    name = name.strip()
    return name

#--------------------------------------------------------------------------------

def get_challenge_preview(data):
    '''Get preview for a given challenge'''
    preview = data['model']['preview']
    return preview

#--------------------------------------------------------------------------------

def save(path, content):
    '''Save content at path, creating parent directories if necessary'''

    solution = os.path.join(path, "solution")
    tests = os.path.join(path, "tests")

    for item in (path, solution, tests):
        if not os.path.isdir(item):
            os.makedirs(item)

    filename = os.path.join(path, "challenge.md")

    with open(filename, 'w') as fd:
        try:
            fd.writelines(content)
        except:
            print "    %s: %s" % (filename, "Puke! Vomit!")

#--------------------------------------------------------------------------------

def main():
    tracks = get_tracks()
    for track in tracks:
        chapters = get_chapters_in_track(track)
        for chapter in chapters:
            slug = chapter['slug']
            chapter_name = chapter['name']
            print "[ %-24s ]--------------------------------------------------" % (chapter_name)
            challenges = get_challenges_in_chapter(track,slug)
            for challenge in challenges:
                slug = challenge['slug']
                data = get_challenge_data(slug)
                challenge_name = get_challenge_name(data)
                challenge_preview = get_challenge_preview(data)
                challenge_content = get_challenge_body(data)
                challenge_content = ("%s\n\n" % challenge_preview) + challenge_content
                challenge_content = ("# %s\n\n" % challenge_name) + challenge_content
                challenge_path = os.path.join("results", track, chapter_name, challenge_name)
                save(challenge_path, challenge_content)
                print "    %s" % (challenge_name)
            print

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#--------------------------------------------------------------------------------
