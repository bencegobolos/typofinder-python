#!/usr/bin/python

import sys
import os
import re
import fnmatch
import argparse
import subprocess


# Get input: source directory of users guide.
def get_input():
    desc = 'Check for misspelled word in your plain text files.'
    epilog = 'Script is made to check for typos automatically ' \
             'in the users guide\'s repository.'
    ap = argparse.ArgumentParser(description=desc, epilog=epilog)
    ap.add_argument('-d', '--dictionary',
                    help='define a dictionary (in .json format) which contains '
                         'the known words (\'htc-dictionary.json\' is given by default).',
                    type=str, default='htc-dictionary.json', metavar='DICTIONARY')
    ap.add_argument('-o', '--output',
                    help='log file which contains the checked files and '
                         'the found typos (\'HDP-1335.log\' is given by default).',
                    type=str, default='HDP-1335.log', metavar='OUTPUT')
    ap.add_argument('input', help='A file or a dictionary you want to check.',
                    metavar='INPUT')

    return ap.parse_args()


def check_input(args):
    if not os.path.exists(args.input):
        sys.stderr.write('ERROR: \'%s\' file or directory does not exists!\n'
                         'Use option -h for more information\n' % args.input)
        sys.exit(1)

    if not os.path.exists(args.input) or not re.match("^[a-zA-Z0-9-]+\.json$", args.dictionary):
        sys.stderr.write('ERROR: \'%s\' dictionary does not exists!\n'
                         'Use option -h for more information\n' % args.dictionary)
        sys.exit(1)


# Find .tex files in folder srcdir.
# Returns:
# * texfiles: list, contains the relative paths to .tex files.
def find_texfiles(srcdir):
    texfiles = []

    for root, directories, files in os.walk(srcdir):
        for file in fnmatch.filter(files, '*.tex'):
            texfiles.append(os.path.join(root, file))

    return texfiles


def exec_dir(command, args):
    texfiles = find_texfiles(args.input)
    log_content = ""
    for file_name in texfiles:
        log_content += ("Executing \'corrector.py\' on file: %s\n" % file_name)
        log_content += subprocess.check_output(command + [file_name])
    dump(log_content, args.output)


def exec_file(command, args):
    dump(subprocess.check_output(command + [args.input]), args.output)


def scan_log_file(log_file):
    with open(log_file) as f:
        content = f.readlines()
    for line in content:
        if re.match("^Unknown word(.)+", line):
            return False

    return True


# Output content(param 1) into file(param 2)
def dump(content, file):
    f = open(file, 'w')
    for line in content:
        f.write(line)
    f.close()


def main():
    args = get_input()

    check_input(args)

    script_path = os.path.dirname(os.path.abspath(__file__))
    command = ['python']
    command.append(os.path.join(script_path, 'corrector.py'))
    command.append(os.path.join(script_path, args.dictionary))

    if os.path.isdir(args.input):
        exec_dir(command, args)
    else:
        exec_file(command, args)

    return scan_log_file(args.output)

if __name__ == "__main__":
    main()
