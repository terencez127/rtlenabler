#!/usr/local/bin/python
import os
import sys
import re

pattern_padding = '.*android:paddingStart=.+'
pattern_close = '([\s]*)[^\s].*/>[\s]*'

reg_padding = re.compile(pattern_padding)
reg_close = re.compile(pattern_close)

file_postfix = '_temp'


def process_xml(path):
    modified = False
    
    with open(path, 'r') as f:
        new_file = open(path + file_postfix, 'w+')
        for line in f:
            found = False
            m = reg_padding.match(line)
            if m is not None:
                found = True
                pos = line.find('.*/>[\s]*')
                m = reg_close.match(line)
                if pos > -1:
                    new_file.write(line[0:pos] + line[pos + 2:])
                modified = True
            if not found:
                new_file.write(line)
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
        print 'Usage: rn your/layout/path'
        exit(0)

    for root, dirs, files in os.walk(folder):
        for f in files:
            process_xml_new(os.path.join(root, f))