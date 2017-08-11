#!/usr/bin/env python3
import datetime
import glob
import os
import hachoir.editor
import hachoir.parser
import hachoir.stream
from hachoir.field import MissingField

import parse
import extract

def locate_fields_by_subpath(parser, subpath):
    def recursive_search(atom, retlist=[]):
        try:
            cd = atom[subpath]
            retlist.append(cd)
        except MissingField:
            pass
        try:
            for x in atom:
                retlist = recursive_search(x, retlist)
        except KeyError as e:
            pass
        return retlist
    return recursive_search(parser)


def locate_creation_date_fields(parser):
    return locate_fields_by_subpath(parser, 'creation_date')

def change_timestamp(incoming, outgoing):
    parser = hachoir.parser.createParser(incoming)

    data = extract.extract(parser)

    editor = hachoir.editor.createEditor(parser)
    output = hachoir.stream.FileOutputStream(outgoing)

    for atom in locate_creation_date_fields(parser):
        cd = editor[atom.path]
        cd.value = parse.get_time(data)

    with output:
        editor.writeInto(output)

def test_timestamp(incoming):
    parser = hachoir.parser.createParser(incoming)
    editor = hachoir.editor.createEditor(parser)
    for atom in locate_creation_date_fields(parser):
        cd = editor[atom.path]
        print(incoming)
        print(cd.value)

def make_edit(folder):
    for file in glob.glob(folder + "*.MP4"):
        change_timestamp(file, "./vids_new/" + file[7:-4] + "_new.MP4")

    for file in glob.glob(folder + "*.MP4"):
        os.remove(file)

def make_test(folder):
    for file in glob.glob(folder + "*.MP4"):
        test_timestamp(file)

if __name__ == '__main__':
    import sys
    folder = "./vids/"
    folder_new = "./vids_new/"
    make_edit(folder)
    # make_test(folder_new)
