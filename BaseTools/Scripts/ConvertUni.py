## @file
#  Check a patch for various format issues
#
#  Copyright (c) 2015, Intel Corporation. All rights reserved.<BR>
#
#  SPDX-License-Identifier: BSD-2-Clause-Patent
#

from __future__ import print_function

VersionNumber = '0.1'
__copyright__ = "Copyright (c) 2015, Intel Corporation  All rights reserved."

import argparse
import codecs
import os
import sys

class ConvertOneArg:
    """Converts utf-16 to utf-8 for one command line argument.

       This could be a single file, or a directory.
    """

    def __init__(self, utf8, source):
        self.utf8 = utf8
        self.source = source

        self.ok = True

        if not os.path.exists(source):
            self.ok = False
        elif os.path.isdir(source):
            for (root, dirs, files) in os.walk(source):
                files = filter(lambda a: a.endswith('.uni'), files)
                for filename in files:
                    path = os.path.join(root, filename)
                    self.ok &= self.convert_one_file(path)
                    if not self.ok:
                        break

                if not self.ok:
                    break
        else:
            self.ok &= self.convert_one_file(source)

    def convert_one_file(self, source):
        new_enc, old_enc = ('utf-8', 'utf-16') if self.utf8 else ('utf-16', 'utf-8')
        with open(source, mode='rb') as f:
            file_content = f.read()
        #
        # Detect UTF-16 Byte Order Mark at beginning of file.
        #
        bom = (file_content.startswith(codecs.BOM_UTF16_BE) or
               file_content.startswith(codecs.BOM_UTF16_LE))
        if bom != self.utf8:
            print(f"{source}: already {new_enc}")
            return True

        #
        # Decode old string data
        #
        str_content = file_content.decode(old_enc, 'ignore')

        #
        # Encode new string data
        #
        new_content = str_content.encode(new_enc, 'ignore')

        with open(source, mode='wb') as f:
            f.write(new_content)
        print(f"{source}: converted, size", len(file_content), '=>', len(new_content))
        return True


class ConvertUniApp:
    """Converts .uni files between utf-16 and utf-8."""

    def __init__(self):
        self.parse_options()
        sources = self.args.source

        self.ok = True
        for patch in sources:
            self.process_one_arg(patch)

        self.retval = 0 if self.ok else -1

    def process_one_arg(self, arg):
        self.ok &= ConvertOneArg(self.utf8, arg).ok

    def parse_options(self):
        parser = argparse.ArgumentParser(description=__copyright__)
        parser.add_argument(
            '--version', action='version', version=f'%(prog)s {VersionNumber}'
        )
        parser.add_argument('source', nargs='+',
                            help='[uni file | directory]')
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--utf-8",
                           action="store_true",
                           help="Convert from utf-16 to utf-8 [default]")
        group.add_argument("--utf-16",
                           action="store_true",
                           help="Convert from utf-8 to utf-16")
        self.args = parser.parse_args()
        self.utf8 = not self.args.utf_16

if __name__ == "__main__":
    sys.exit(ConvertUniApp().retval)
