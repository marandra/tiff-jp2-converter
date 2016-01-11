#!/usr/bin/env python2.7
import argparse
import ConfigParser
import logging
import logging.handlers
from apscheduler.schedulers.background import BackgroundScheduler
import time
import glob
import os
import sys
import subprocess
from pprint import pprint #only for development
#from sh import rsync
import tiff2jp2 #only for development

def get_settings():
    #defaults
    configfile = './datamover.ini'
    sectname = 'config'
    settings = {'incoming_target': "./incoming",
                'buffer_dir':      "",
                'outgoing_target': "./outgoing",
                'log_file':        "./default.log", 
                'dry_run':         "", 
    }

    #parse args (now, in case there is an alternate config file)
    argparser = argparse.ArgumentParser(description='Move data from A to B.')
    argparser.add_argument('-f', '--config',    default = configfile, help='use alternate configuration file')
    argparser.add_argument('--incoming_target', help='')
    argparser.add_argument('--outgoing_target', help='')
    argparser.add_argument('--buffer_dir',      help='')
    argparser.add_argument('--log_file',        help="log activity to specified FILE")
    argparser.add_argument('-n', '--dry-run', action="store_const", const="--dry-run", help="perform a trial run with no changes made")
    argparser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = vars(argparser.parse_args())

    #parse configuration file and update settings
    configparser = ConfigParser.SafeConfigParser()   
    configparser.read(args['config'])
    if configparser.has_section(sectname):
        for candidate in settings:
            if configparser.has_option(sectname, candidate):
                settings[candidate] = configparser.get(sectname, candidate)

    #update setting with argument options 
    for key in settings:
        if args[key]:
            settings[key] = args[key]
    
    return settings

def filestoprocess(path, format):
    #list of files to process
    list0 = glob.glob("{}/*{}*".format(path, format))
    list0.sort(key=os.path.getmtime, reverse=False)
    #if there are many files, return all but the last 2 of them
    #or empty if no files
    if len(list0) > 2 or len(list0)==0:
        files = list0[:-2]
    #if there two left return the older, so the newer has time to be closed.
    #if there is only one, return it
    elif len(list0) > 0:
        files = [list0[0]]
        
    return files

def move_tiff_tobuffer():
    # set up logging
    logger = logging.getLogger("move_tiff_tobuffer")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    #get values from settings
    dorigin = settings['incoming_target']
    dbuff = settings['buffer_dir']
    dryrun = settings['dry_run']

    #get list of files to process
    files = filestoprocess(dorigin, "tif")

    #move them to buffer directory
    #print time.time() #debug
    #print files #debug
    for file in files:
        time.sleep(1) #debug
        command = "{} {} {} {} {}".format("rsync", "-a --remove-source-files", dryrun, file, dbuff)
        out = subprocess.check_output(command.split())
        logger.info("{} moved to buffer directory".format(file.split("/")[-1]))
    return

def image_conversion():
    # set up logging
    logger = logging.getLogger("image_conversion")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    #get values from settings
    dbuff = settings['buffer_dir']
    dryrun = settings['dry_run']
    
    #get list of files to process
    files = filestoprocess(dbuff, "tif")

    #convert tiff images to jp2
    for fnt in files:
        #convert tiff to jp2
        bmp = tiff2jp2.tiff2jp2(fnt)
        logger.info("{} converted to .jp2".format(fnt.split("/")[-1]))
        #create thumbnail
        bmp = tiff2jp2.tiff2jp2thumb(fnt, bmp, 200)
        logger.info("{} thumbnail created".format(fnt.split("/")[-1]))

        #dummy jp2 conversion
        #time.sleep(1)
        #command = "{} {} {} {} {}".format("rsync", "-a --remove-source-files", dryrun, file, file.split(".")[0]+".jp2")
        #out = subprocess.check_output(command.split())

    return

def move_jp2_todest():
    # set up logging
    logger = logging.getLogger("move_jp2_todest")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    #get values from settings
    dbuff = settings['buffer_dir']
    ddest = settings['outgoing_target']
    dryrun = settings['dry_run']

    #get list of files to process
    files = filestoprocess(dbuff, "jp2")

    #move them to buffer directory
    for file in files:
        time.sleep(1) #debug
        command = "{} {} {} {} {}".format("rsync", "-a --remove-source-files", dryrun, file, ddest)
        out = subprocess.check_output(command.split())
        logger.info("{} moved to dest directory".format(file.split("/")[-1]))

    return

def systemcheck():
    if not os.access(settings['incoming_target'], os.R_OK):
        print "Cannot access incoming dir."
        return 1
    if not os.access(settings['outgoing_target'], os.W_OK):
        print "Cannot access outgoing dir."
        return 1
    if not os.access(settings['buffer_dir'], os.W_OK):
        print "Cannot access buffer dir."
        return 1
    so = os.statvfs(settings['outgoing_target'])
    sb = os.statvfs(settings['buffer_dir'])
    spaceo = so.f_bavail * so.f_frsize / 1024
    spaceb =  sb.f_bavail * sb.f_frsize / 1024
    if spaceo < 1000000: 
        print "Not enough space."
        return 1
    if spaceb < 1000000: 
        print "Not enough space."
        return 1
    return 0

######################################################################
#main
if __name__ == "__main__":

    #set up options
    settings = get_settings()

    #system health check before starting (can read, can write, enough space)
    if systemcheck():
        print "Aborting."
        sys.exit(-1)

    #set up logging
    #logging.basicConfig(loglevel=logging.WARNING)
    handler = logging.handlers.RotatingFileHandler(settings['log_file'], maxBytes=1000000, backupCount=1)
    FORMAT = "%(asctime)s : %(levelname)-4s : %(name)-18s : %(message)s"
    handler.setFormatter(logging.Formatter(FORMAT, datefmt='%Y-%m-%d %H:%M:%S'))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    #set up scheduler
    scheduler = BackgroundScheduler()
    #interval should be longer than writing time for file
    scheduler.add_job(move_tiff_tobuffer, 'interval', seconds=10)
    scheduler.add_job(image_conversion, 'interval', seconds=5)
    scheduler.add_job(move_jp2_todest, 'interval', seconds=10)
    scheduler.start()

    try:
        logger.info('Started')
        while True:
            time.sleep(1000)
            logger.info('Waiting')
        
    except (KeyboardInterrupt, SystemExit):
    #    #pass
        scheduler.shutdown()
        logger.info('Canceled')
