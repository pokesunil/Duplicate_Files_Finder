#! /usr/bin/env python

# Originally taken from:
# http://www.pythoncentral.io/finding-duplicate-files-with-python/
# Original Auther: Andres Torres

# Adapted to only compute the md5sum of files with the same size

'''
Usage examples:
  python duplicates_finder.py "C:/Pictures"
  python duplicates_finder.py -s 5 "C:/Pictures"
'''

import argparse
import os
import sys
import hashlib
import time


def find_duplicates(folders, size):
    """
    Takes in an iterable of folders and prints & returns the duplicate files
    """
    dup_size = {}
    for i in folders:
        # Iterate the folders given
        if os.path.exists(i):
            # Find the duplicated files and append them to dup_size
            join_dicts(dup_size, find_duplicate_size(i, size))
        else:
            print('%s is not a valid path, please verify' % i)
            sys.exit()

    print('Comparing files with the same size...')
    dups = {}
    for dup_list in dup_size.values():
        if len(dup_list) > 1:
            join_dicts(dups, find_duplicate_hash(dup_list))
    print_results(dups)
    return dups


def find_duplicate_size(parent_dir, size):
    # Dups in format {hash:[names]}
    dups = {}
    for dirName, subdirs, fileList in os.walk(parent_dir):
        # print('Scanning %s...' % dirName)
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            fs = os.stat(path).st_size
            if fs > size:
                # Check to make sure the path is valid.
                if not os.path.exists(path):
                    continue
                # Calculate sizes
                file_size = os.path.getsize(path)
                # Add or append the file path
                if file_size in dups:
                    dups[file_size].append(path)
                else:
                    dups[file_size] = [path]
    return dups


def find_duplicate_hash(file_list):
    # print('Comparing: ')
    # for filename in file_list:
        # print('    {}'.format(filename))
    dups = {}
    for path in file_list:
        file_hash = hashfile(path)
        if file_hash in dups:
            dups[file_hash].append(path)
        else:
            dups[file_hash] = [path]
    return dups


# Joins two dictionaries
def join_dicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]


# Calculate MD5 hash of a file
def hashfile(path, blocksize=65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def print_results(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print('Duplicates Found:')
        print(
            'The following files are identical. The name could differ, but the'
            ' content is identical'
            )
        print('___________________')
        for result in results:
            for subresult in result:
                print('\t\t%s' % subresult)
            print('___________________')

    else:
        print('No duplicate files found.')


def main():
    parser = argparse.ArgumentParser(description='Find duplicate files')
    parser.add_argument(
        'folders', metavar='dir', type=str, nargs='+',
        help='A directory to parse for duplicates'
        )
    parser.add_argument(
        '-s', '--size', nargs='?', const=1, default=1, type=int,
        help='file size in MBs'
        )
    args = parser.parse_args()

    # Track the performance of the program
    start_time = time.time()

    # File size is converted to bytes
    file_size_in_bytes = abs(args.size) * 1024 * 1024

    find_duplicates(args.folders, file_size_in_bytes)

    print("Time Taken: %s seconds" % round((time.time() - start_time), 2))
    if abs(args.size) > 1:
        print("file size specified was: %s MB" % abs(args.size))


if __name__ == '__main__':
    main()
