# import required packages
import pandas as pd
from colorama import Fore, Back, Style
from pathlib import Path
import traceback as tb
from scipy import stats
import numpy as np

# create main dataframe that will hold data for all participant. This will be replaced by an existing file is 'mount' command by user
DATA = pd.DataFrame(columns=['MVC max', 'DLS mean', 'SLS mean', 'DLS %', 'SLS %'], index=['Name'])

# export DATA into a csv. User must include ".csv". can make folders if path specified does not exist
def Export(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path)

# returns a dataframe containing a xlsx, csv, or txt file. Takes file path and a bool indicating if the data already has correct formatting
def FileMounter(path, YNformated=False):    
    match YNformated:
        case True:
            if(path[-5:] == '.xlsx'):
                return (pd.read_excel(path, index_col=0))
            elif(path[-4:] == '.csv' or path[-4] == '.txt'):
                return (pd.read_csv(path, index_col=0))
            else:
                raise(ImportError(Fore.RED + "file type not supported. Please double check you typed the path correctly." + Style.RESET_ALL))
        case False:    
            if(path[-5:] == '.xlsx'):
                return (pd.read_excel(path))
            elif(path[-4:] == '.csv' or path[-4] == '.txt'):
                return (pd.read_csv(path))
            else:
                raise(ImportError(Fore.RED + "file type not supported. Please double check you typed the path correctly." + Style.RESET_ALL))    

# Takes files output by PowerLab and formats them to be compatible with this analyzer
def DataFormater(dataframe):
       cutdata = dataframe.iloc[5: , :2]
       cutdata.columns = ['Time', 'mVs']
       print (cutdata)
       return cutdata

# take a dataframe and a column name with in that data frame and returns the higest aboslute value in that column
def FindGreatestValue(dataframe, columnName):
    return max([abs(num) for num in dataframe[columnName].tolist()])

# take a dataframe and a column name with in that data frame and returns the mean of the aboslute values in that column
def FindAbsMean(dataframe, columnName):
    absolutes = [abs(num) for num in dataframe[columnName].tolist()]
    return sum(absolutes) / len(absolutes)

# take a subcommand (tack) that specifies if a DLS or SLS is to be normalized and add the normalized data to DATA
def Normalize(tack):
    for i in (i for i in DATA.index if pd.isnull(DATA.loc[i, tack + ' %'])):
        DATA.loc[i, tack + ' %'] = DATA.loc[i, tack + ' mean'] / DATA.loc[i, 'MVC max']
  
# run a standard 2 way t-test given 2 list of data and the names of the lists. Prints t-test to a text file   
def TTest(array1: list, array2: list, arrayname1: str, arrayname2: str):
    tTest = stats.ttest_ind(array1, array2)
    print (tTest)
    tTestString = 'statistic: ' + str(getattr(tTest, 'statistic')) + '\np-value: ' + str(getattr(tTest, 'pvalue')) + '\ndegrees of freedom: ' + str(getattr(tTest, 'df'))
    with open('t-test_' + arrayname1.replace(' ', '_') + '_vs_' + arrayname2.replace(' ', '_') + '.txt', 'w') as text_file:
        text_file.write(tTestString)


# Fills a cell at a particular index (participant name) and column with a given value. Also takes a bool to allow the function to overwrite existing cell value
def AddEntry(participant, valueName, value, YNrewrite):
    global DATA
    try:
        if (not YNrewrite and pd.isnull(DATA.loc[participant, valueName])):
            DATA.loc[participant, valueName] = value
    except KeyError:
        if (not YNrewrite):
            DATA.loc[participant, valueName] = value
    try:
        if (not YNrewrite and not pd.isnull(DATA.loc[participant, valueName])):
            print('The cell you are trying to add data to already contains a value')
    except:
        DATA.loc[participant, valueName] = value
    if (YNrewrite):
            DATA.loc[participant, valueName] = value

# coordinates new data entery
def AddRun(currentCommand, path, participant): # TODO clean this up
    match currentCommand:
        case 'MVC' | 'MVC -R'| 'DLS' | 'DLS -R' | 'SLS' | 'SLS -R':
            tempData = FileMounter(path)
            tempData = DataFormater(tempData)
            match currentCommand:
                case 'MVC':
                    AddEntry(participant, 'MVC max', FindGreatestValue(tempData, 'mVs'), False)
                case 'MVC -R':
                    AddEntry(participant, 'MVC max', FindGreatestValue(tempData, 'mVs'), True)
                case 'DLS':
                    AddEntry(participant, 'DLS mean', FindAbsMean(tempData, 'mVs'), False)
                case 'DLS -R':
                    AddEntry(participant, 'DLS mean', FindAbsMean(tempData, 'mVs'), True)
                case 'SLS':
                    AddEntry(participant, 'SLS mean', FindAbsMean(tempData, 'mVs'), False)
                case 'SLS -R':
                    AddEntry(participant, 'SLS mean', FindAbsMean(tempData, 'mVs'), True)  
        case 'MVC -M' | 'DLS -M' | 'SLS -M':
            subcommand = input('Enter a comma separated list of paths to the ' 
                               + currentCommand.split(' -')[0] 
                               + ' files you would like to add followed a | and a comma separated list of the names belonging to each ' 
                               + currentCommand.split(' -')[0] 
                               + " in order. For example, '"
                               + currentCommand.split(' -')[0]
                               + '1.xlsx, '
                               + currentCommand.split(' -')[0]
                               + "2.xlsx | mark, bob': \n").split(' | ')
            print(subcommand)
            subpaths = subcommand[0].split(', ')
            print(subpaths)
            subnames = subcommand[1].split(', ')
            print(subnames)
            print(range(len(subpaths)))
            for i in range(len(subpaths)):
                tempData = FileMounter(subpaths[i])
                tempData = DataFormater(tempData)
                match currentCommand:
                    case 'MVC -M':
                        AddEntry(subnames[i], 'MVC max', FindGreatestValue(tempData, 'mVs'), False)
                    case 'DLS -M':
                        AddEntry(subnames[i], 'DLS mean', FindAbsMean(tempData, 'mVs'), False)
                    case 'SLS -M':
                        AddEntry(subnames[i], 'SLS mean', FindAbsMean(tempData, 'mVs'), False)

# removes a cell or a row depening on if it is passed a string or a list
def Clear(pos):
    global DATA
    match pos:
        case list():
            DATA.loc[pos[0], pos[1]] = np.NaN
            print('Data at ' + pos[0] + ', ' + pos[1] + 'was removed')
        case str():
            DATA = DATA.drop(pos, axis=0)
            print('column ' + pos + ' was removed')




# Prints a list of commands
def PrintHelp():
    print('''What would you like to do? 
          Here is a list of commands: 
          'help' (print this list again)
          'mount' (if you have a master data file you have been using, this comands allows you to import it)
          'MVC' or 'DLS' or 'SLS' (import and add MVC/DLS/SLS data. Add -R to allow this command to rewrite cells; add an -M to import multiple files of the same type at once)
          'addSubj' (add MVC, DLS, and SLS and run all normalization for a new participant)
          'normalize' (normalizes DLS or SLS means to MVC max. Use -DLS or -SLS to indicate what needs to be normalized)
          't-test' (run a standard t-test between two columns of data. outputs to a .txt file)
          'clear' (remove a cell (w/ -C) or an entire participant (w/ -P))
          'show' (print the entire mounted data. add -S to only show a several line summery)
          'export'
          'quit' (stop the program)
          ''')
#print list of commands on start up
PrintHelp()

#start main program loop to allow user to input multiple commands
loop = True
while loop:
    #get command for this loop
    currentCommand = input('\nEnter your command here: ')

    ## command handler
    try:
        match currentCommand:
            case 'mount':
                DATA = FileMounter(input('Ender the path to the file holding the data you are processing:\n'), True)                   
                print ('file mounted')
                print(DATA)
            case 'MVC' | 'MVC -R'| 'DLS' | 'DLS -R' | 'SLS' | 'SLS -R'|'MVC -M' | 'DLS -M' | 'SLS -M':
                AddRun(currentCommand, path=input('Enter the path to the ' + currentCommand.split(' -')[0] + ' file you would like to add: \n'), 
                       participant=input('Enter the full name of the participant for whom you are adding a ' + currentCommand.split(' -')[0]))
            case 'normalize -DLS' | 'normalize -SLS':
                Normalize(currentCommand.split('-')[-1])
            case 't-test':
                subcommand = input('Please enter the names of the columns you would like to compare separated with commas:\n').split(', ')
                TTest(DATA[subcommand[0]].dropna().tolist(), DATA[subcommand[1]].dropna().tolist(), subcommand[0], subcommand[1])
            case 'addSubj': # TODO better way to do this?
                subcommand = input('Please enter the name of the participant you would like to add followed by the MVC, DLS, and SLS as a comma sparated list:\n').split(', ')
                AddRun('MVC', subcommand[1], subcommand[0])
                AddRun('DLS', subcommand[2], subcommand[0])
                AddRun('SLS', subcommand[3], subcommand[0])
                Normalize('DLS')
                Normalize('SLS')
            case 'clear -C' | 'clear -P':
                subcommand = currentCommand.split('-')[-1]
                match subcommand:
                    case'C':
                        Clear(input('enter the the participant name and column of the cell you want to erase separated by a comma:\n').split(', '))
                    case 'P': 
                        Clear(input('enter the participants name you want to remove:\n'))

                        
            case 'export':
                Export(DATA, input('Please enter the path and file name you would like: \n'))
            case 'help':
                PrintHelp()
            case 'show':
                print(DATA.to_string())
            case 'show -S':
                print(DATA)
            case 'quit':
                loop = False
            case _: 
                print(Fore.RED + 'The command was not recognized' + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + 'an error has occured:' + Style.RESET_ALL)
        print (Fore.RED + tb.format_exc() + Style.RESET_ALL)
        
