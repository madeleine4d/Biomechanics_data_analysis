# TODO: 
# add a ClearCell() function
#

# import required packages
import pandas as pd
from colorama import Fore, Back, Style
from pathlib import Path
import traceback as tb
from scipy import stats

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
        
# Take two lists and the nemes of those lists and generated a .txt file with the output of a t-test between the means of the two lists
def TTest(array1: list, array2:list, arrayname1: str, arrayname2: str):
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

# Prints a list of commands
def PrintHelp():
    print('''What would you like to do? 
          Here is a list of commands: 
          'help' (print this list again)
          'mount' (if you have a master data file you have been using, this comands allows you to import it)
          'MVC' or 'DLS' or 'SLS' (import and add MVC/DLS/SLS data. Add -R to allow this command to rewrite cells; add an -M to import multiple files of the same type at once)
          'normalize' (normalizes DLS or SLS means to MVC max. Use -DLS or -SLS to indicate what needs to be normalized)
          'show' (print the entire mounted data. add -S to only show a several line summery)
          'export'
          'quit' (stop the program)
          ''')
# print list of commands on start up
PrintHelp()

# start main program loop to allow user to input multiple commands
loop = True
while loop:
    # get command for this loop
    currentCommand = input('\nEnter your command here: ')

    # command handler
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
            case 'addSubj':
                subcommand = input('Please enter the name of the participant you would like to add followed by the MVC, DLS, and SLS as a comma sparated list:\n').split(', ')
                for path in subcommand[1:3]: AddRun(currentCommand, path, subcommand[0])
                Normalize('-DLS')
                Normalize('-SLS')
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
        
