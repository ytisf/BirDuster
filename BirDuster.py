#!/usr/bin/env python3

import os
import csv
import sys
import base64
import socket
import random
import argparse
import colorama
import requests
import threading
import concurrent.futures

from builtins import input # compatibility, python2/3
from datetime import datetime
from colorama import Fore, Style
from user_agent import generate_user_agent, generate_navigator


# Default configurations
MAX_WORKERS = 13
DEF_TIMEOUT = 3
DEFAULT_DIR_LIST_FILE = 'dir_list.txt'
FOUND = []


def _print_banner():
	banner = Fore.RED + "\n######           ######                                    \n" + Style.RESET_ALL
	banner += Fore.RED + "#     # # #####  #     # #    #  ####  ##### ###### #####  \n" + Style.RESET_ALL
	banner += Fore.RED + "#     # # #    # #     # #    # #        #   #      #    # \n" + Style.RESET_ALL
	banner += Fore.RED + "######  # #    # #     # #    #  ####    #   #####  #    # \n" + Style.RESET_ALL
	banner += Fore.RED + "#     # # #####  #     # #    #      #   #   #      #####  \n" + Style.RESET_ALL
	banner += Fore.RED + "#     # # #   #  #     # #    # #    #   #   #      #   #  \n" + Style.RESET_ALL
	banner += Fore.RED + "######  # #    # ######   ####   ####    #   ###### #    # \n" + Style.RESET_ALL
	banner += Fore.RED + "                                                           \n" + Style.RESET_ALL
	banner += Fore.BLUE + "\tA DirBuster KnockOff for Python2+3\n" + Style.RESET_ALL
	banner += Fore.GREEN + "\tVersion 1.0.\n" + Style.RESET_ALL
	banner += Fore.WHITE + "\tHosted on https://www.github.com/ytisf/BitDuster.\n\n" + Style.RESET_ALL
	print(banner)

def _print_err(message):
	sys.stderr.write(Fore.RED + "[X]"+Style.RESET_ALL+"\t%s\n" % message)

def _print_succ(message):
	sys.stdout.write(Fore.GREEN + "[+]"+Style.RESET_ALL+"\t%s\n" % message)

def _print_info(message):
	sys.stdout.write(Fore.BLUE + "[+]" + Style.RESET_ALL + "\t%s\n" % message)

def _fetch_url(url, headers, ssl_verify=True, write_response=False, timeout=DEF_TIMEOUT):
	global FOUND
	domain = url.split("//")[-1].split("/")[0].split('?')[0].split(':')[0]
	socket.setdefaulttimeout = timeout
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	try:
		site_request = requests.get(url, headers=headers, verify=ssl_verify)
		FOUND.append([dt_string, url, site_request.status_code, len(site_request.content)])
		if write_response:
			file_name_string = "".join(x for x in url if x.isalnum())
			f = open(os.path.join(domain,file_name_string), 'wb')
			f.write(site_request.content)
			f.close()
	except Exception as e:
		FOUND.append([dt_string, url, "Error: %s" % e, 0])
	sys.stdout.write(".")
	sys.stdout.flush()

def parse_arguemnts():
	parser = argparse.ArgumentParser()
	parser.add_argument("domain", help="domain or host to buster")
	parser.add_argument("-v", "--verbosity", action="count", default=0, help="Increase output verbosity")
	parser.add_argument("-p", "--port", help="Which port?", type=int)
	parser.add_argument("-P", "--pfile", help="Port file to iterate")
	parser.add_argument("-t", "--threads", type=int, help="Concurrent threads to run [15]", default=MAX_WORKERS)
	parser.add_argument("-o", "--output", help="Output file to write to")
	parser.add_argument("-l", "--dlist", help="Directory list file")
	parser.add_argument("-w", "--writeresponse", help="Write response to file", action="store_true", default=False)
	parser.add_argument("-i", "--ignorecertificate", help="Ignore certificate errors", action="store_true", default=False)
	parser.add_argument("-u", "--useragent", help="User agent to use.", default=generate_user_agent())
	parser.add_argument("--ssl", help="Should i use SSL?", action="store_true")
	parser.add_argument('--timeout', help="Socket timeout [3]", default=3, type=int)
	args = parser.parse_args()
	if args.port and args.pfile:
		_print_err("Can't have both port file [pfile] and port [port] specified.")
		_print_err("Kindly choose one.")
		exit()
	if args.dlist:
		if not os.path.exists(args.dlist):
			_print_err("Can't find file '%s'." % args.dlist)
			exit()
	if args.pfile:
		if not os.path.exists(args.pfile):
			_print_err("Can't find file '%s'." % args.pfile)
			exit()
	if args.ignorecertificate and not args.ssl:
		_print_info("Since ignore-certificate flag is on but SSL is not, will attempt SSL connection.")
	if not args.output:
		args.output = "%s_output.csv" % args.domain
	if args.verbosity:
		_print_info("Will write output to %s." % args.output)
	if args.verbosity and not args.useragent:
		_print_info("No user-agent was supplied so using '%s'." % args.useragent)

	if os.path.exists(args.output):
		i = input(Fore.RED + "[!]"+Style.RESET_ALL+"\tOutput file exists. Should i overwrite it?[no]:") or False
		if i == False:
			args.output = "%s_%s.csv" % (args.domain, random.randint(111,999))
			_print_info("Set output file to be '%s'." % args.output)
		else:
			_print_info("Original file will be overwritten.")
	return args

def main():
	_print_banner()
	args = parse_arguemnts()

	# Read relevant files
	# Parse ports file.
	if args.pfile:
		ports = []
		ports_raw = open(args.pfile, 'r').readlines()
		for port in ports_raw:
			try:
				dis = port.strip()
				if len(dis) != 0:
					thisport = int()
					ports.append(thisport)
				else:
					# Probably empty line.
					pass
			except:
				_print_err("Error parsing ports file. One of the lines in not an integer.")
				exit()
	elif args.port:
		ports = [args.port]
	elif args.ssl:
		ports = [443]
	else:
		ports = [80]

	# Parse Directory file
	dirs = []
	if args.dlist:
		dirs_raw = open(args.dlist, 'r').readlines()
		for i in dirs_raw:
			thisDir = i.strip()
			if len(thisDir) == 0:
				continue
			dirs.append(thisDir)
	else:
		dirs_raw = open(DEFAULT_DIR_LIST_FILE, 'r').readlines()
		for i in dirs_raw:
			thisDir = i.strip()
			if len(thisDir) == 0:
				continue
			dirs.append(thisDir)

	# Make output directory incase of writing
	if args.writeresponse:
		try:
			os.mkdir(args.domain)
		except:
			# Directory exists
			pass

	# Start threading
	headers = {'User-Agent': args.useragent}
	thread_local = threading.local()
	URLs_to_check = []
	for port in ports:
		for dir in dirs:
			if args.ssl:
				URLs_to_check.append("https://%s:%s/%s" % (args.domain, port, dir))
			else:
				URLs_to_check.append("http://%s:%s/%s" % (args.domain, port, dir))

	_print_info("Starting execution on %s URLs of %s ports and %s directories." % (len(URLs_to_check), len(ports), len(dirs)))
	_print_info("Execution starting with %s threads..." % args.threads)

	thread_args = []
	for i in URLs_to_check:
		thread_args.append((i,headers,args.ignorecertificate,args.writeresponse, args.timeout))

	with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
		executor.map(_fetch_url, *zip(*thread_args))

	_print_succ("Completed exection on %s items." % len(URLs_to_check))

	# Write output to file
	with open(args.output, 'w', newline='') as csvfile:
		fieldnames = ['Datetime', 'URL', 'StatusCode', 'ResponseSize']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		writer.writeheader()
		for item in FOUND:
			thisItem = {'Datetime': item[0], 'URL':item[1], 'StatusCode':item[2], 'ResponseSize': item[3]}
			writer.writerow(thisItem)

	_print_succ("Wrote all items to file '%s'." % args.output)

	exit()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		_print_err("Got keyboard interrupt. Byebye now.")
		exit()
