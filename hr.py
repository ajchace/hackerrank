#!/usr/bin/env python

#--------------------------------------------------------------------------------

# TODO:
#    2. Figure out what writelines() pukes.
#    5. Store URL for each problem description with (in?) problem description.
#    7. Makefile to convert markdown to other formats.
#   10. Add support for command line arguments to list/select/download tracks

# TODONE:
#    1. Fix FIXMEs.
#    3. Put results in directory
#    4. Dynamically create directory structure based on chapter names.
#    6. Better logging.
#    8. virtualenv with requirements.txt
#    9. Add function(s) to get a list of tracks

#--------------------------------------------------------------------------------

import html2text
import json
import logging
import os.path
import requests
import sys

#--------------------------------------------------------------------------------

base_url = "https://www.hackerrank.com/rest/contests/master"

#--------------------------------------------------------------------------------

# Set up logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler(stream=sys.stdout)
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)-9s | %(message)s')
console.setFormatter(formatter)
log.addHandler(console)

#--------------------------------------------------------------------------------

def get_tracks():
    '''Get a dictionary of tracks'''
    # https://www.hackerrank.com/rest/contests/master/tracks/
    log.debug("--------------------------------------------------------------------------------")
    url = base_url + "/tracks/"
    log.debug("Url: " + url)
    response = requests.get(url)
    log.debug("Status: " + response.reason)
    log.debug("Elapsed time: " + str(response.elapsed))
    data = response.json()
    tracks = data['models']
    return tracks

#--------------------------------------------------------------------------------

def get_chapters_in_track(track):
    '''Get a dictionary of chapters for a given track'''
    # https://www.hackerrank.com/rest/contests/master/tracks/python/chapters/
    log.debug("--------------------------------------------------------------------------------")
    url = base_url + "/tracks/" + track + "/chapters"
    log.debug("Url: " + url)
    response = requests.get(url)
    log.debug("Status: " + response.reason)
    log.debug("Elapsed time: " + str(response.elapsed))
    data =response.json()
    chapters = data['models']
    return chapters

#--------------------------------------------------------------------------------

def get_challenges_in_chapter(track, slug):
    '''Get a dictionary of challenges in a chapter'''
    # "https://www.hackerrank.com/rest/contests/master/categories/python|py-introduction/challenges"
    log.debug("--------------------------------------------------------------------------------")
    url = base_url + "/categories/" + track + "|" + slug + "/challenges" 
    log.debug("Url: " + url)
    response = requests.get(url)
    log.debug("Status: " + response.reason)
    log.debug("Elapsed time: " + str(response.elapsed))
    data = response.json()
    challenges = data['models']
    return challenges

#--------------------------------------------------------------------------------

def get_challenge_data(slug):
    # "https://www.hackerrank.com/rest/contests/master/challenges/py-hello-world" 
    log.debug("--------------------------------------------------------------------------------")
    url = base_url + "/challenges/" + slug
    log.debug("Url: " + url)
    response = requests.get(url);
    log.debug("Status: " + response.reason)
    log.debug("Elapsed time: " + str(response.elapsed))
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
        challenge_name = data['model']['name']
        log.exception("Unable to parse data for challenge " + challenge_name)

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
            #fd.writelines(content.splitlines())
            fd.writelines(content)
        except:
            log.warning("Type: " + str(type(content)))
            log.warning("Attempting to convert unicode string to sequence of strings")
            try:
                lines = [ line.encode('utf-8') + '\n' for line in content.splitlines() ]
                fd.writelines(lines)
            except:
                log.exception("Unable to save " + filename)

#--------------------------------------------------------------------------------

def main():
    tracks = get_tracks()
    for track in tracks:
        track_slug = track['slug']
        track_name = track['name']
        log.debug("Track: " + track_name)
        chapters = get_chapters_in_track(track_slug)
        for chapter in chapters:
            chapter_slug = chapter['slug']
            chapter_name = chapter['name']
            log.debug("Chapter: " + chapter_name)
            challenges = get_challenges_in_chapter(track_slug,chapter_slug)
            for challenge in challenges:
                challenge_slug = challenge['slug']
                challenge_data = get_challenge_data(challenge_slug)
                challenge_name = get_challenge_name(challenge_data)
                challenge_preview = get_challenge_preview(challenge_data)
                challenge_content = get_challenge_body(challenge_data)
                challenge_content = ("%s\n\n" % challenge_preview) + challenge_content
                challenge_content = ("# %s\n\n" % challenge_name) + challenge_content
                challenge_path = os.path.join("results", track_name, chapter_name, challenge_name)
                save(challenge_path, challenge_content)
                log.debug("Challenge: " + challenge_name)
                log.info("%s: %s: %s" % (track_name, chapter_name, challenge_name))

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#--------------------------------------------------------------------------------
