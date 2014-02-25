#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2014 Hervé BREDIN (http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import subprocess
import os


class CommandWrapper(object):

    """
    Parameters
    ----------
    command : str
        Command (e.g. ls, mkdir or ffmpeg)
    exists_params : iterable, optional
        Parameters passed to command when checking its existence.
        This parameters was introduced to deal with commands that
        do real things even when no parameters are given (e.g. vobcopy needs
        parameter -h to avoid copying DVD)
    """

    def __init__(self, command, exists_params=None):
        super(CommandWrapper, self).__init__()

        # make sure exists_params is a (potentially empty) list
        if exists_params is None:
            exists_params = []
        exists_params = list(exists_params)

        if self.command_exists(command, exists_params):
            self.command = command

        else:
            message = 'Could not find command "{command}"'
            raise ValueError(message.format(command=command))

    @classmethod
    def command_exists(cls, command, exists_params):
        """Check whether `command` exists

        >>> CommandWrapper.command_exists('ls')
        True
        >>> CommandWrapper.command_exists('sl')
        False
        >>> CommandWrapper.command_exists('/bin/ls')
        True
        """

        try:
            with open(os.devnull, mode='w') as _:
                subprocess.Popen(
                    [command] + exists_params,
                    stdout=_, stderr=_
                ).communicate()
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                return False
        return True

    def run_command(self, options=None, env=None):
        """
        Parameters
        ----------
        options : iterable, optional
        env : dict, optional
        """

        if options is None:
            options = []
        else:
            options = list(options)

        cmd = [self.command] + options

        try:
            with open(os.devnull, mode='w') as _:
                subprocess.check_call(cmd, stderr=_, stdout=_, env=env)

        except Exception, e:
            raise e  # TODO: better handling
