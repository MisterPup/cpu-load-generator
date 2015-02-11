# Copyright 2012 Anton Beloglazov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" A tool for generating a set of subsequent CPU utilization levels.
"""

from optparse import OptionParser, Option, IndentedHelpFormatter
import os
import subprocess
import time
import psutil

def process(interval, utilization_list, ncpus, fixed_mem_util):
    free_mem = psutil.virtual_memory().free #bytes
    occupy_mem = free_mem*fixed_mem_util/100
    occupy_mem_str = str(occupy_mem)
    ncpus_str = str(ncpus)

    print ncpus_str
    print occupy_mem_str
	

    for utilization in utilization_list:
        utilization_str = str(utilization)
        print "\nSwitching to " + utilization_str + "%"
        if ncpus != 0:
            p = subprocess.Popen(['/usr/local/bin/lookbusy',
                                  '--ncpus', ncpus_str,
                                  '--cpu-util', utilization_str,
                                  '--mem-util', occupy_mem_str])
        else:
            p = subprocess.Popen(['/usr/local/bin/lookbusy',
                                  '--cpu-util', utilization_str,
                                  '--mem-util', occupy_mem_str])

        time.sleep(interval)
        p.terminate()


class PosOptionParser(OptionParser):

    def format_help(self, formatter=None):
        class Positional(object):
            def __init__(self, args):
                self.option_groups = []
                self.option_list = args

        positional = Positional(self.positional)
        formatter = IndentedHelpFormatter()
        formatter.store_option_strings(positional)
        output = ['\n', formatter.format_heading('Positional Arguments')]
        formatter.indent()
        pos_help = [formatter.format_option(opt) for opt in self.positional]
        pos_help = [line.replace('--', '') for line in pos_help]
        output += pos_help
        return OptionParser.format_help(self, formatter) + ''.join(output)

    def add_positional_argument(self, option):
        try:
            args = self.positional
        except AttributeError:
            args = []
        args.append(option)
        self.positional = args

    def set_out(self, out):
        self.out = out


def main():
    parser = PosOptionParser(
        usage='Usage: python %prog [options] INTERVAL SOURCE',
        description='Generates a set of subsequent ' +
                    'CPU utilization levels read from a file. ' +
                    '                                         ' +
                    'Copyright (C) 2012 Anton Beloglazov. ' +
                    'Released under Apache 2.0 license.')
    parser.add_positional_argument(
        Option('--INTERVAL', action='store_true',
               help='interval between subsequent CPU ' +
               'utilization levels in seconds'))
    parser.add_positional_argument(
        Option('--SOURCE', action='store_true',
               help='source file containing a new line ' +
               'separated list of CPU utilization levels ' +
               'specified as numbers in the [0, 100] range'))
    parser.add_option('-n', '--ncpus', type='int', dest='ncpus', default=0,
                      help='number of CPU cores to utilize [default: autodetect]')

    parser.add_option('-m', '--mem-util', type='int', dest='fixed_mem_util', default=0,
                      help='percentage of free ram to occupy [default: 0]')

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error('incorrect number of arguments')

    try:
        interval = int(args[0])
    except ValueError:
        parser.error('interval must be an integer >= 0')
    if interval <= 0:
        parser.error('interval must be an integer >= 0')

    filename = args[1]
    if not os.access(filename, os.R_OK):
        parser.error('cannot read file: ' + filename)

    utilization = []
    for line in open(filename):
        if line.strip():
            try:
                n = float(line)
                if n < 0 or n > 100:
                    raise ValueError
                utilization.append(int(n))
            except ValueError:
                parser.error('the source file must only ' +
                             'contain new line separated ' +
                             'numbers in the [0, 100] range')

    if interval <= 0:
        parser.error('interval must be an integer >= 0')

    process(interval, utilization, options.ncpus, options.fixed_mem_util)


if __name__ == '__main__':
    main()
