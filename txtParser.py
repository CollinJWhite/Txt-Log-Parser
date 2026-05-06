import os
import logging
import re
logging.basicConfig(filename='myProgramLog.txt', filemode='w', level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

#ask for path to txt file
#check fortwo things - if that file exists (ask user if they wanna try again) and whether the file they input is a txt
#open file and start reading lines
#add read in what kind of message and count, saving the line for an error or failiure

#-------------------Functions-----------------------------------------------------------
def build_regexes():
    logging.info('Building regexes for different logging types')
    #make regexes for different logging types
    regex_list = []

    basic_regex = ("basic", re.compile(r'\[([A-Z]+)\] (.*)$')) 
    #group 1 = type, group 2 = message
    regex_list.append(basic_regex)

    python_regex = ("python", re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}),(\d{3}) - ([A-Z]+)- (.*)$'))
    #group 1 = date, group 2 = time, group 3 = milliseconds, group 4 = logging type, group 5 = message
    regex_list.append(python_regex)

    log4j_regex = ("log4j", re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}),(\d{3}) ([A-Z]+)\s+(\[[\w\d\-]+\] [\w\.\-]+) - (.*)$'))
    #group 1 = date, group 2 = time, group 3 = milliseconds, group 4 = logging type, group 5 = logging app, group 6 = message
    regex_list.append(log4j_regex)

    serilog_regex = ("serilog", re.compile(r'^\[(\d{2}:\d{2}:\d{2}) ([A-Z]+)\] (.*)$'))
    #group 1 = time, group 2 = logging type, group 3 = message
    regex_list.append(serilog_regex)

    syslog_regex = ("syslog", re.compile(r'^(\w{3} \d{2}) (\d{2}:\d{2}:\d{2}) (\w+) ([\w\d\[\]]+): ([A-Z]+): (.*)$'))
    #group 1 = date, group 2 = time, group 3 = hostname, group 4 = process name, group 5 = logging type, group 6 = message
    regex_list.append(syslog_regex)

    return regex_list

def match_regex(file, regex_list):
    logging.info('Matching regex to file')
    pos = file.tell()
    first_line = file.readline()
    file.seek(pos)

    for name, regex in regex_list:
        logging.debug(f'Testing {name} regex')
        if regex.match(first_line):
            logging.info(f'Matched {name} regex')
            return regex, name
        
    #if no regexes match, log critical and return None
    logging.critical('No regexes matched the file format. Cannot process file.')
    return None

def process_file(directory, loggingCounts, errorMessages, criticalMessages):
    logging.info('Processing file.')
    with open(directory, "r", encoding="utf-8") as f:
        regex_list = build_regexes()
        regex, name = match_regex(f, regex_list)
        for line in f:
            logging_type = process_line(line, regex, name, errorMessages, criticalMessages)
            loggingCounts[logging_type] += 1
    

def process_line(line, regex, name, errorMessages, criticalMessages):
    logging.debug(f'Processing line {line}')
    regexed_line = regex.match(line)
    if(line != f'\n'):

        #process line based on regex type
        message = ''
        match name:
            case 'basic':
                logKind = regexed_line.group(1)
                message = regexed_line.group(2)
            case 'python':
                logKind = regexed_line.group(4)
                message = regexed_line.group(5)
            case 'log4j':
                logKind = regexed_line.group(4)
                match logKind:
                    case 'WARN':
                        logKind = 'WARNING'
                    case 'FATAL':
                        logKind = 'CRITICAL'
                message = regexed_line.group(6)
            case 'serilog':
                logKind = regexed_line.group(2)
                message = regexed_line.group(3)
            case 'syslog':
                logKind = regexed_line.group(5)
                message = regexed_line.group(6)
                match logKind:
                    case 'INF':
                        logKind = 'INFO'
                    case 'WRN':
                        logKind = 'WARNING'
                    case 'ERR':
                        logKind = 'ERROR'
                    case 'FTL':
                        logKind = 'CRITICAL'

        match logKind:
            case 'INFO':
                return 0
            case 'WARNING':
                return 1
            case 'ERROR':
                errorMessages.append(message)
                return 2
            case 'CRITICAL':
                criticalMessages.append(message)
                return 3
            case _:
                logging.critical(f'LOGGING TYPE NOT FOUND; Found type: {logKind}')
                return -1

def output_results(loggingCounts, errorMessages, criticalMessages):
    print('---------- Summary ----------\n')
    print(f'Info Logs: {loggingCounts[0]}')
    print(f'Warning Logs: {loggingCounts[1]}')
    print(f'Error Logs: {loggingCounts[2]}')
    print(f'Critical Logs: {loggingCounts[3]}\n')
    if(loggingCounts[2] > 0):
        print(f'-----Error Messages-----\n{errorMessages}\n')
    if(loggingCounts[3] > 0):
        print(f'-----Critical Messages-----\n{criticalMessages}\n')




#-------------------Start of main program-----------------------------------------------
logging.info('Start of program')

validFile = False
directory=''
while(not validFile):
    directory = input('Please enter a txt file to scan (include the .txt). Enter \'q\' to quit: ')
    if(directory == 'q'):
        logging.debug('Quitting due to user input...')
        break
    logging.debug(f'Validating path %s', directory)
    directoryStrLength = len(directory)
    if(os.path.isfile(directory)):
        if(directory[directoryStrLength-4:directoryStrLength] == '.txt'):
            validFile = True
        else:
            basename = os.path.basename(directory)
            logging.warning('User tried using this file: %s. Prompting Again.', basename)
            print(f'{basename} is not a .txt file. Try Again.')
    else:
        logging.warning('User gave an invalid file path: %s. Prompting Again.', directory)
        print('Invalid file path. Try Again.')

if(directory != 'q'):
    logging.info('Got valid .txt file')
    logging.debug('Processing logs...')

    #build regexes for logging
    basic_regex = re.compile(r'^\[(\w+)\]\s*(.*)$') #group 1 = type, group 2 = message
    

    #lists of logging type counts and messages, INFO, WARNING, ERROR, CRITICAL
    loggingCounts = [0, 0, 0, 0]
    errorMessages = []
    criticalMessages = []
    process_file(directory, loggingCounts, errorMessages, criticalMessages)
    output_results(loggingCounts, errorMessages, criticalMessages)

logging.info('End of program')