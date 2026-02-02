import os
import logging
import re
logging.basicConfig(filename='myProgramLog.txt', filemode='w', level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')

#ask for path to txt file
#check fortwo things - if that file exists (ask user if they wanna try again) and whether the file they input is a txt
#open file and start reading lines
#add read in what kind of message and count, saving the line for an error or failiure

#-------------------Functions-----------------------------------------------------------
def process_file(directory, loggingCounts, errorMessages, criticalMessages):
    logging.info('Processing file.')
    with open(directory, "r", encoding="utf-8") as f:
        for line in f:
            logging_type = process_line(line)
            loggingCounts[logging_type] += 1
    

def process_line(line):
    logging.debug(f'Processing line {line}')
    loggingRegex = re.compile(r'INFO|WARNING|ERROR|CRITICAL')
    logKind = loggingRegex.search(line)
    if(line != f'\n'):
        match logKind.group():
            case 'INFO':
                return 0
            case 'WARNING':
                return 1
            case 'ERROR':
                return 2
            case 'CRITICAL':
                return 3
            case _:
                logging.critical(f'LOGGING TYPE NOT FOUND; Found type: {logKind.group()}')
                return -1

def output_results(loggingCounts, errorMessages, criticalMessages):
    print('---------- Summary ----------\n')
    print(f'Info Logs: {loggingCounts[0]}')
    print(f'Warning Logs: {loggingCounts[1]}')
    print(f'Error Logs: {loggingCounts[2]}')
    print(f'Critical Logs: {loggingCounts[3]}\n')


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
    #lists of logging type counts and messages, INFO, WARNING, ERROR, CRITICAL
    loggingCounts = [0, 0, 0, 0]
    errorMessages = []
    criticalMessages = []
    process_file(directory, loggingCounts, errorMessages, criticalMessages)
    output_results(loggingCounts, errorMessages, criticalMessages)

logging.info('End of program')