#!/usr/bin/env python
# Author: Venkat Cherukupali
# Date: 12 Feb 2017
#
# This script creates local repository directories and rsync's data from remote
# repos: This dictionary contains mapping of remote mirror details
#

from subprocess import Popen,PIPE,STDOUT
import os,os.path
import sys

# Local root dir for local_repo to be rsycned into
local_repo_root_dir = '/pub'

# repo name
repo_name = 'centos'

# repo version
repo_version = '7.3.1611'

# rsync binary
rsync = '/usr/bin/rsync'

# rsync options
rsync_opts = '-avzS'

# This hash contains all repos ro be rsynced
repos = { 'os': 'rsync://mirror.math.princeton.edu/pub/centos/7.3.1611/os/x86_64',
	  'updates': 'rsync://mirror.math.princeton.edu/pub/centos/7.3.1611/updates/x86_64',
	  'extras': 'rsync://mirror.math.princeton.edu/pub/centos/7.3.1611/extras/x86_64'
	  }

def create_if_not_present(ldir):
	"""
	Check and create dir, if not present
	if present as file, bail out
	"""
	if os.path.exists(ldir) and os.path.isdir(ldir):
		return True
	elif os.path.exists(ldir) and not os.path.isdir(ldir):
		print ldir,"is not a directory"
		sys.exit(1)
	else:
		os.makedirs(ldir)

def run_cmd(cmd):
	"""
	Run cmd and bail out if error
	"""
	#print "Running",' '.join(cmd)
	p = Popen(cmd,stdout=PIPE,stderr=STDOUT,shell=False)
	(out,err) = p.communicate()
	if p.returncode != 0:
		print "Command:",' '.join(cmd), "failed"
		print out
		sys.exit(1)
	else:
		parse_mail(out)

def parse_mail(out):
	"""
	Parse and mail output
	"""
	data = []
	for l in out.splitlines():
		if l.startswith('x86_64'):
			data.append(l)
	print '\n'.join(data)



def sync_repo(remote,remote_repo):
	"""
	rsync remote_repo
	"""
	local_dir = local_repo_root_dir + '/' + repo_name + '/' + repo_version + '/'
	local_dir = local_dir + remote
	create_if_not_present(local_dir)
	print "Repo:",remote
	rsync_cmd = [rsync,rsync_opts,'--delete',remote_repo,local_dir]
	run_cmd(rsync_cmd)

# Main
for repo in repos:
	sync_repo(repo,repos[repo])
