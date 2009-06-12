#! /usr/bin/python

__author__="David Avsajanishvili"
__date__ ="$Jun 11, 2009 1:47:38 PM$"

import sys, re

def usage(errstr=None):
    if errstr:
        sys.stderr.write(errstr)
    sys.stderr.write("""
NAME

    %(file)s - Marks changes as [option="changed"] in ASCIIDOC
                        source file according on diff in RCS format

SYNOPSIS

    %(file)s -h
    %(file)s --help
    %(file)s ASCIIDOC_FILE DIFF_FILE

DESCRIPTION

   The %(file)s command finds changed sections in ASCIIDOC source file
   according on RCS-formatted DIFF_FILE and marks them with
   [option="changed"] attribute. The diff could be obtained by executing
   following command:

       diff -Bbn ASCIIDOC_FILE ASCIIDOC_FILE_OLD > DIFF_FILE

   NOTE: The ASCIIDOC_FILE must be first (left) file in the diff.

   The command writes result to standard output (STDOUT).
   If DIFF_FILE is "-", the diff is got from standard input (STDIN).

AUTHOR

   David Avsajanishvili <avsd05@gmail.com>

COPYING

   Copyright (C) 2009 David Avsajanishvili. Free use of this software is
   granted under the terms of the GNU General Public License (GPL).

""" % {'file' : 'asciidoc-markdiff'})
    return #end of USAGE


def get_diff(difftext):
    """
    Parses difftext and returns tuple of two dictionaries --
    DIFF_ADDS and DIFF_DELS. Each dictionary has format:
    {line:numberoflines}
    """

    DIFF_ADDS = {}
    DIFF_DELS = {}

    rgA = re.compile(r"^a(\d+)\s+(\d+)\s*$",re.M)
    rgD = re.compile(r"^d(\d+)\s+(\d+)\s*$",re.M)

    for m in rgA.finditer(difftext):
        (lne, lns) = m.groups()
        DIFF_ADDS[int(lne)] = int(lns)
        
    for m in rgD.finditer(difftext):
        (lne, lns) = m.groups()
        DIFF_DELS[int(lne)] = int(lns)

    #sys.stderr.write(repr(DIFF_ADDS))
    #sys.stderr.write(repr(DIFF_DELS))
    return (DIFF_ADDS,DIFF_DELS)

def is_line_changed(lineno, DIFF_ADDS, DIFF_DELS):
    """
    Returns True, if according on DIFF_ADDS and DIFF_DELS
    the line is changed. Otherwise - False
    """

    if DIFF_ADDS.has_key(lineno):
        return True

    for k in DIFF_DELS.keys():
        if lineno >= k and lineno < k + DIFF_DELS[k]:
            return True
    return False

def f_write(s):
    """
    Writes result
    """
    sys.stdout.write(s)

def mark_file(srcfile, DIFF_ADDS, DIFF_DELS):
    """
    Marks diffs in file, specified in srcfile.
    Writes result using f_write (currently to STDOUT)
    """

    LN = 0 #Line number
    is_changed = False #Flag that section is changed
    curline = "" #Current line
    out_buff = [] #Output buffer (array of lines)
    eos_next = False

    sect_wr = "" #Section wrapper and corresponding regexp:
    sect_re = re.compile(r"^(--|---+|\+\+\++|\.\.\.+|\*\*\*+|___+|===+|///+)\s*$")

    def write_changes():
        
        if is_changed:

            # Find that there is something in this
            # section except comments and blank lines
            for i in out_buff:
                i = i.strip()
                if not (i=="" or i[:2]=="//"):
                    f_write('[options="changed"]\n')
                    break

        for i in out_buff:
            f_write(i)
    

    f = open(srcfile)
    try:

        # Reading first line
        curline = f.readline()
        LN +=1

        # Iterating
        while(curline): 

            # Checking end of section
            end_of_sect = False

            if sect_wr:
                if curline == sect_wr:
                    eos_next = True
                    sect_wr = ""
            else:
                if curline.strip() != "" and out_buff \
                    and (out_buff[-1].strip() == ""):
                    end_of_sect = True

                if eos_next and curline.strip()!="":
                    end_of_sect = True
                    eos_next = False

                # Suppress wrapped sections 
                if sect_re.search(curline):
                    if not (out_buff):
                        sect_wr = curline
                    elif abs(len(out_buff[-1]) - len(curline)) < 3\
                            and (not out_buff[-1][0] in "[."):
                        eos_next = True
                    else:
                        sect_wr = curline

            if end_of_sect:
                write_changes()
                out_buff = []
                is_changed = False
                eos_next=False

            out_buff.append(curline)
            is_changed = is_changed or is_line_changed(LN, DIFF_ADDS, DIFF_DELS)                         

            # Reading the next line
            curline = f.readline()
            LN +=1

        write_changes()
        
    finally:
        f.close()


def execute(srcfile, difffile):

    difftext = ""
    # Getting diff dictionaries
    if difffile == "-":
        while(True):
            t = sys.stdin.readline()
            if not(t):
                break
            difftext+=t
    else:
        f = open(difffile)
        difftext = f.read()
        f.close()

    (DIFF_ADDS, DIFF_DELS) = get_diff(difftext)

    mark_file(srcfile, DIFF_ADDS, DIFF_DELS)
    return




if __name__ == "__main__":
    # Process command line options.
    import getopt
    try:
        opts,args = getopt.getopt(sys.argv[1:],
            'h',
            ['help'])
    except getopt.GetoptError:
        usage('Illegal command options')
        sys.exit(1)

    for o,v in opts:
        if o in ('--help','-h'):
            usage()
            sys.exit(1)

    if len(args) != 2:
        usage("Illegal number of arguments")
        sys.exit(1)

    execute(args[0],args[1])
    exit(0)


