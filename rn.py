#!/usr/local/bin/python
import os
import sys
import re

# pattern_margin_padding = '(.*android:padding|.*android:layout_margin)(Left|Right)(=.+)'
pattern_gravity = '(.*)(left|right)(.*)'

pair_dict = {'left': 'start', 'right': 'end'}

# reg_margin_padding = re.compile(pattern_margin_padding)
reg_gravity = re.compile(pattern_gravity)

file_postfix = '_temp'

flags = ['layout_alignParentLeft', 'layout_alignParentRight', 'layout_alignLeft', 'layout_alignRight', 'layout_toLeftOf', 'layout_toRightOf', 'paddingLeft', 'paddingRight', 'layout_marginLeft', 'layout_marginRight']


#  Absolute parameters flags, if find one of them, set the corresponding parameter to True.
#  If they are True, ignore the corresponding relative parameters in the same tag.
flag_dict = {}

PREFIX_LENGTH = 8  # Now it's length of string 'android:'


def reset_flags():
    for key in flags:
        flag_dict[key] = False


def handle_value(line, start, new_file, tag, postfix, tag_start):
    m = reg_gravity.match(line, start)
    if m is not None and line.find(pair_dict[m.group(2)], start) == -1:
    #if m is not None:
        new_line = line[:start] + m.group(1) + pair_dict[m.group(2)] + '|' + m.group(2) + m.group(3) + '\n'
        new_file.write(new_line)
        return True, True
    return False, False


def handle_key(line, start, new_file, tag, postfix, tag_start):
    modified = False
    if postfix is None:
        postfix = ''
    index = line.find('=', start)
    if index > 0:
        found = False
        if line[index-4-len(postfix):index] == 'Left' + postfix:
            new_tag = tag + 'Start' + postfix
            tag += "Left" + postfix
            found = True
        elif line[index-5-len(postfix):index] == 'Right' + postfix:
            new_tag = tag + 'End' + postfix
            tag += "Right" + postfix
            found = True
        if found:
            if not flag_dict[tag]:
                end_pos = line.find('>', start)
                if end_pos != -1:
                    if line[end_pos-1] == '/':
                        print 'Found />:  ', line
                        new_line = line[:tag_start] + new_tag + line[index:end_pos-1] + '\n'
                    else:
                        print 'Found >:  ', line
                        new_line = line[:tag_start] + new_tag + line[index:end_pos] + '\n'
                else:
                    new_line = line[:tag_start] + new_tag + line[index:]
                new_file.write(new_line)
                flag_dict[tag] = True
                modified = True
            new_file.write(line)
            return True, modified

        if line[index-5-len(postfix):index] == 'Start' + postfix:
            tag += 'Left' + postfix
            found = True
        elif line[index-3-len(postfix):index] == 'End' + postfix:
            tag += 'Right' + postfix
            found = True
        if found:
            if not flag_dict[tag]:
                new_file.write(line)
                flag_dict[tag] = True
            else:
                end_pos = line.find('>', start)
                if end_pos != -1:
                    if line[end_pos-1] == '/':
                        print 'Found />:  ', line
                        new_file.write(' '*(tag_start-PREFIX_LENGTH) + '/>\n')
                    else:
                        print 'Found >:  ', line
                        new_file.write(' '*(tag_start-PREFIX_LENGTH) + '>\n')
            return True, modified
    return False, False


def process_xml_new(path):
    modified = False
    reset_flags()
    with open(path, 'r') as f:
        new_file = open(path + file_postfix, 'w+')
        for line in f:
            written = False
            end = False
            change = False
            if line.find('>') > -1:
                end = True

            index = line.find('android:')
            if index != -1:
                tag = ''
                start = index + 8
                tag_start = start
                index = line.find('layout_', start)
                if index != -1: # layout_
                    tag += 'layout_'
                    start = index + 6
                    index = line.find('margin', start)
                    if index != -1: # layout_margin
                        tag += 'margin'
                        written, change = handle_key(line, index, new_file, tag, '', tag_start)
                    else:
                        index = line.find('align', start)
                        if index!= -1: # layout_align
                            tag += "align"
                            start = index + 5
                            index = line.find('Parent', start)
                            if index != -1: # layout_alignParent
                                tag += 'Parent'
                                written, change = handle_key(line, index, new_file, tag, '', tag_start)
                            else:
                                written, change = handle_key(line, index, new_file, tag, '', tag_start)
                        else:
                            index = line.find('to', start)
                            if index != -1: # layout_to
                                tag += 'to'
                                written, change = handle_key(line, index, new_file, tag, 'Of', tag_start)
                            else:
                                index = line.find('gravity=', start)
                                if index != -1: # layout_gravity
                                    tag += 'gravity='
                                    index += 8
                                    written, change = handle_value(line, index, new_file, tag, '', tag_start)
                else:   # padding
                    if line.startswith('padding=', start):
                        index = start + 8
                        tag += 'padding='
                        written, change = handle_key(line, index, new_file, tag, '', tag_start)
                    elif line.startswith('gravity=', start):
                        index = start + 8
                        tag += 'gravity='
                        written, change = handle_value(line, index, new_file, tag, '', tag_start)

            if end:
                reset_flags()

            if not written:
                new_file.write(line)
            modified = modified or change
        new_file.close()
    if modified:
        os.remove(path)
        os.rename(path + file_postfix, path)
        print 'Modified:  ' + path
    else:
        os.remove(path + file_postfix)


if __name__ == '__main__':
    try:
        folder = sys.argv[1]
    except:
        print 'Usage: rn.py your/layout/path'
        exit(0)

    for root, dirs, files in os.walk(folder):
        for f in files:
            process_xml_new(os.path.join(root, f))