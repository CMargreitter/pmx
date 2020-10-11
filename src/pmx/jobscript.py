#!/usr/bin/env python

# pmx  Copyright Notice
# ============================
#
# The pmx source code is copyrighted, but you can freely use and
# copy it as long as you don't change or remove any of the copyright
# notices.
#
# ----------------------------------------------------------------------
# pmx is Copyright (C) 2006-2013 by Daniel Seeliger
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name of Daniel Seeliger not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# DANIEL SEELIGER DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS.  IN NO EVENT SHALL DANIEL SEELIGER BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------

"""jobscript generation
"""

import os
import sys
import types
import re
import logging
from glob import glob

class Jobscript:
    """Class for jobscript generation

    Parameters
    ----------
    ...

    Attributes
    ----------
    ....

    """

    def __init__(self, **kwargs):

        self.queue = 'SGE' # could be SLURM
        self.simtime = 24 # hours
        self.simcpu = 2 # CPU default
        self.bGPU = True
        self.fname = 'jobscript'
        self.jobname = 'jobName'
        self.modules = []
        self.source = []
        self.export = []
        self.cmds = [] # commands to add to jobscript
        self.gmx = None
        self.header = ''
        self.cmdline = ''
        
        for key, val in kwargs.items():
            setattr(self,key,val)                 
             
    def create_jobscript( self ):
        # header
        self._create_header()
        # commands
        self._create_cmdline()
        # write
        self._write_jobscript()    
        
    def _write_jobscript( self ):
        fp = open(self.fname,'w')
        fp.write(self.header)
        fp.write(self.cmdline)
        fp.close()
            
    def _add_to_jobscriptFile( self ):
        fp = open(self.fname,'a')
        fp.write('{0}\n'.format(cmd))
        fp.close()           
            
    def _create_cmdline( self ):
        if isinstance(self.cmds,list)==True:
            for cmd in self.cmds:
                self.cmdline = '{0}{1}\n'.format(self.cmdline,cmd)
        else:
            self.cmdline = cmds
            
    def _create_header( self ):
        moduleline = ''
        sourceline = ''
        exportline = ''
        for m in self.modules:
            moduleline = '{0}\nmodule load {1}'.format(moduleline,m)
        for s in self.source:
            sourceline = '{0}\nsource {1}'.format(sourceline,s)
        for e in self.export:
            exportline = '{0}\export load {1}'.format(exportline,e)
        gpuline = ''
        if self.bGPU==True:
            gpuline = '#$ -l gpu=1'
        gmxline = ''
        if self.gmx!=None:
            gmxline = 'export GMXRUN="{gmx} -ntomp {simcpu} -ntmpi 1"'.format(gmx=self.gmx,simcpu=self.simcpu)            
            
        if self.queue=='SGE':
            self._create_SGE_header(moduleline,sourceline,exportline,gpuline,gmxline)
        elif self.queue=='SLURM':
            self._create_SLURM_header(moduleline,sourceline,exportline,gpuline,gmxline)
        
    def _create_SGE_header( self,moduleline,sourceline,exportline,gpuline,gmxline ):    
        self.header = '''#$ -S /bin/bash
#$ -N {jobname}
#$ -l h_rt={simtime}:00:00
#$ -cwd
#$ -pe *_fast {simcpu}
{gpu}

{source}
{modules}
{export}

{gmx}
'''.format(jobname=self.jobname,simcpu=self.simcpu,simtime=self.simtime,gpu=gpuline,
           source=sourceline,modules=moduleline,export=exportline,
           gmx=gmxline)
        
        
    def _create_SLURM_header( self,moduleline,sourceline,exportline,gpuline,gmxline):
        fp = open(self.fname,'w')

        self.header = '''#!/bin/bash
#SBATCH --job-name={jobname}
#SBATCH --get-user-env
#SBATCH -N 1
#SBATCH -n {simcpu}
#SBATCH -t {simtime}:00:00

{source}
{modules}
{export}

{gmx}
'''.format(jobname=self.jobname,simcpu=self.simcpu,simtime=self.simtime,
           source=sourceline,modules=moduleline,export=exportline,
           gmx=gmxline)
    
