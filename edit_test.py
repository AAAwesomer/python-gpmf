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

def processed_files(folder):
    filelist = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            filelist.append(file)
    return filelist

def test_edit(folder, folder_new):
    for file in glob.glob(folder + "*.MP4"):
        change_timestamp(file, folder_new + file[7:-4] + "_new.MP4")

def make_edit(folder, folder_new):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".MP4"):
                print(os.path.join(root,file))
                print("{parent}processed{child}".format(parent=root[:25], child=os.path.join(root, file)[34:]))
                if file not in processed_files(folder_new):
                    change_timestamp(
                        os.path.join(root,file),
                        "{parent}processed{child}".format(
                            parent=root[:25], child=os.path.join(root,file)[34:]
                        )
                    )

def make_test(folder):
    for file in glob.glob(folder + "*.MP4"):
        test_timestamp(file)

if __name__ == '__main__':
    import sys
    folder = "/media/aarni/My Passport/rr_videos"
    folder_new = "/media/aarni/My Passport/processed"

    # make_edit(folder, folder_new)
    # test_edit("./vids/", "./vids_new/")
    make_test("./vids_new/")
    make_test("./vids/")
    # print([i for i in os.listdir(folder) if i.endswith(".MP4")])




