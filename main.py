#!/usr/bin/env python3
from __future__ import print_function
from __future__ import division
import re
import psutil
import keyboard
import sys, os
from sys import platform
import time
import rumps
from ScriptingBridge import *
from AppKit import NSWorkspace
import getpass
from subprocess import Popen, PIPE
import webbrowser

def ioreg_battery_info():
	output = Popen(["ioreg", "-r", "-k", "LegacyBatteryInfo", "-w", "0"], stdout=PIPE).communicate()[0]
	try: # python3 try
		return str(output, encoding='utf-8')
	except TypeError: # python2 error handling
		return output

def parse_ioreg_dict(output): return dict([(kw.strip().strip('"'), vw.strip()) for kw, vw in [line.split("=", 1) for line in output.split('\n') if line.find('=')>0]])

def is_two_complement_negative(value): return value > (2**63-1)
def two_complement(value): return 2**64 - value

def fix_negative(value):
	if is_two_complement_negative(value):
		return -two_complement(value)
	else:
		return value

def ioreg_battery_dict(): return parse_ioreg_dict(ioreg_battery_info())
def fix_integer(string): return fix_negative(int(string))

def format_time(string):
	minutes = int(string)
	if minutes == 65535:
		return None
	else:
		return "%s:%s" % (minutes//60, minutes%60)

def percentage(ratio): return "%s%%" % (int(ratio*100))

humanize_index = {
		"Time Remaining": format_time,
		"Average Time To Empty": format_time,
		"Average Time To Full": format_time,
		"Instant Time To Empty": format_time,
		"Full To Empty Time": format_time,
		"Wear Ratio": percentage,
		"Charge Ratio": percentage,}

def humanize_data(k, v):
	if k in humanize_index:
		return humanize_index[k](v)
	else:
		return v

def wear_ratio(info):
	return int(info["MaxCapacity"]) / int(info["DesignCapacity"])

def charge_ratio(info):
	return int(info["CurrentCapacity"]) / int(info["MaxCapacity"])

def full_to_empty_time(info):
	if get_data(info, "Amperage") < 0:
		return -int(info["MaxCapacity"])*60 / get_data(info, "Amperage")
	else:
		return 65535

synthetize_index = {
		"Amperage": lambda i: fix_integer(i["Amperage"]),
		"InstantAmperage": lambda i: fix_integer(i["InstantAmperage"]),
		"WearRatio": wear_ratio,
		"ChargeRatio": charge_ratio,
		"FullToEmptyTime": full_to_empty_time,
		}

def synthetize_data(battery_info, k):
	if k in synthetize_index:
		return synthetize_index[k](battery_info)

def get_data(battery_info, k):
	if k in synthetize_index:
		return synthetize_data(battery_info, k)
	elif k in battery_info:
		return battery_info[k]
	else:
		raise KeyError("%s" % k)

keys_to_show = [
		"Temperature",
		"CycleCount",
		"DesignCapacity",
		"MaxCapacity",
		"WearRatio",
		"CurrentCapacity",
		"ChargeRatio",
		"Voltage",
		"Amperage",
		"InstantAmperage",
		"InstantTimeToEmpty",
		"TimeRemaining",
		"AvgTimeToEmpty",
		"AvgTimeToFull",
		"FullToEmptyTime",
		]

def print_key_value(k, v):
	if v is not None:
		print("%s = %s" % (k, v))

battery_info =  ioreg_battery_dict()
keysNow = [(k, humanize_data(k, get_data(battery_info, k))) for k in keys_to_show]

# Options
@rumps.clicked('About')
def clean_up_before_quit(_):
	webbrowser.get('open -a /Applications/Google\ Chrome.app %s').open('https://www.github.com/VladUsatii')

@rumps.clicked('Quit App')
def clean_up_before_quit(_):
	rumps.quit_application()



if __name__ == "__main__":
	if platform == "darwin":
		batteryinfo = ioreg_battery_info()
		cpuUsage = psutil.virtual_memory().percent
		cpuAvail = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
		app = rumps.App("Heatdeck", title='Heatdeck', quit_button=None)
		app.menu = [
			"Used memory: " + str(int(cpuUsage)) + "%",
			"Free memory: " + str(int(cpuAvail)) + "%",
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[0][0]) + ": " + str(keysNow[0][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[1][0]) + ": " + str(keysNow[1][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[2][0]) + ": " + str(keysNow[2][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[3][0]) + ": " + str(keysNow[3][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[4][0]) + ": " + str(keysNow[4][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[5][0]) + ": " + str(keysNow[5][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[6][0]) + ": " + str(keysNow[6][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[7][0]) + ": " + str(keysNow[7][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[8][0]) + ": " + str(keysNow[8][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[9][0]) + ": " + str(keysNow[9][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[10][0]) + ": " + str(keysNow[10][1]),
			re.sub(r"(\w)([A-Z])", r"\1 \2", keysNow[10][0]) + ": " + str(keysNow[11][1]),
			None
	]
		app.run()
	else:
		sys.exit()
