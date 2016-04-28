'''
Created on 16 juil. 2013

ouvre une boite de dialogue

@author: Lenovo
source: http://tkinter.unpythonic.net/wiki/tkFileDialog
'''
def import_conc_boot_h1(time_tag, path):
    import csv
    open_file = csv.reader(open(path + "hypothese_1_bootstrap" + time_tag +  ".csv",'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    for row in open_file:
        if first_row == 1:
            first_row = 0
            nb_iter = len(row) - 2
            continue
        if len(str(row[0])) < 6:
            continue
        for i in range(len(row)):
            row[i]=row[i].replace(',','.')
        dict_data.setdefault(str(row[1]), {})
        dict_data[str(row[1])][str(row[0])] = {"h1_boot_conc_" + str(i) : float(row[i + 2]) for i in range(nb_iter)}
    data=[dict_data,len(dict_data), nb_iter]
    return data

def import_conc_boot_h2(time_tag, path):
    import csv
    open_file = csv.reader(open(path + "hypothese_2_bootstrap" + time_tag +  ".csv",'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    for row in open_file:
        if first_row == 1:
            first_row = 0
            nb_iter = len(row) - 2
            continue
        for i in range(len(row)):
            row[i]=row[i].replace(',','.')
        dict_data.setdefault(str(row[1]), {})
        dict_data[str(row[1])][str(row[0])] = {"h2_boot_conc_" + str(i) : float(row[i + 2]) for i in range(nb_iter)}
    data=[dict_data,len(dict_data), nb_iter]
    return data

def import_EF(time_tag, path):
    import csv
    open_file = csv.reader(open(path + "EF_inh_cancer_bootstrap" + time_tag +  ".csv",'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    for row in open_file:
        if first_row == 1:
            first_row = 0
            nb_iter = len(row) - 2
            continue
        dict_data.setdefault(row[0], {'flag_c' : row[2], 'main_EF_c' : row[1].replace(',','.'), 'boot_c' : {}})
        for i in range(len(row) - 3):
            dict_data[row[0]]['boot_c'][i] = row[i + 3].replace(',','.')
    open_file = csv.reader(open(path + "EF_inh_non_cancer_bootstrap" + time_tag +  ".csv",'rb'), delimiter=';')
    first_row = 1
    for row in open_file:
        if first_row == 1:
            first_row = 0
            nb_iter = len(row) - 3
            continue
        if row[0] not in dict_data:
            print row[0]
            print"effor, missing EF"
            quit()
        dict_data[row[0]]['boot_nc'] = {}
        dict_data[row[0]]['flag_nc'] = row[2]
        dict_data[row[0]]['main_EF_nc'] = row[1].replace(',','.')
        for i in range(len(row) - 3):
            dict_data[row[0]]['boot_nc'][i] = row[i + 3].replace(',','.')
    data=[dict_data,len(dict_data), nb_iter]
    return data

def import_severity(time_tag, path):
    import csv
    open_file = csv.reader(open(path + "severity" + time_tag +  ".csv",'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    nb_iter = 0
    for row in open_file:
        if first_row == 1:
            first_row += 1
            continue
        if first_row == 2:
            first_row = 0
            dict_data.setdefault('main',[row[1].replace(',','.'), row[2].replace(',','.')])
            dict_data.setdefault('boot',{})
            continue
        dict_data['boot'][nb_iter] = [row[1].replace(',','.'), row[2].replace(',','.')]
        nb_iter += 1
    data=[dict_data,len(dict_data), nb_iter]
    return data

def import_main_results():
    import Tkinter, tkFileDialog
    import csv
    import os
    directory = os.pardir
    filename = os.path.join(directory,'maitrise', 'results_art1')
    root= Tkinter.Tk()
    root.withdraw()
    file_opt = options = {}
    options['defaultextension'] = '.csv'
    options['filetypes'] = [('csv', '.csv')]
    options['initialdir'] = filename
    options['initialfile'] = "main_results" + ".csv"
    options['parent'] = root
    options['title'] = "Select the h1 bootstrap output file from art1 code"
    file_path = tkFileDialog.askopenfilename(**file_opt)
    time_tag = file_path.split("main_results")[1].split(".csv")[0]
    open_file = csv.reader(open(file_path,'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    for row in open_file:
        if first_row == 1:
            first_row = 0
            continue
        if row[8] == 'na':
            continue
        for i in range(len(row)):
            row[i]=row[i].replace(',','.')
        dict_data.setdefault(str(row[1]), {})
        dict_data[str(row[1])][str(row[0])] = {'tot_hours' : int(row[2]), 'Flag_EF_c' : row[3], 'Flag_EF_nc' : row[4], 'measured_concentrations' : int(row[5]), 'Positive_measured_concentrations' : int(row[6]), 'concentration' : float(row[8]), 'breathing_rate' : float(row[9]), 'intake_per_h' : float(row[10])}
    data=[dict_data,len(dict_data), time_tag, file_path.split("main_results")[0]]
    return data


def import_conversion():
    import Tkinter, tkFileDialog
    import csv
    root= Tkinter.Tk()
    root.withdraw()
    file_opt = options = {}
    options['defaultextension'] = '.csv'
    options['filetypes'] = [('csv', '.csv')]
    options['initialdir'] = 'D:\\programmation\workspace\eclipse\maitrise\results'
    options['initialfile'] = "conversion_matrix" + ".csv"
    options['parent'] = root
    options['title'] = "Select the conversion matrix from initial classification to IO"
    file_path = tkFileDialog.askopenfilename(**file_opt)
    open_file = csv.reader(open(file_path,'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    for row in open_file:
        if first_row == 1:
            first_row = 2
            continue
        if first_row == 2:
            IO_sectors = row
            first_row = 0
            continue
        for i in range(len(row) - 1):
            if float(row[i + 1].replace(',','.')) == 0:
                dict_data.setdefault(str(IO_sectors[i + 1]), {})
                continue
            else:
                dict_data.setdefault(str(IO_sectors[i + 1]), {})
                dict_data[str(IO_sectors[i + 1])][str(row[0])] = float(row[i + 1].replace(',','.'))
    return dict_data


def import_B_matrix():
    import Tkinter, tkFileDialog
    import csv
    root= Tkinter.Tk()
    root.withdraw()
    file_opt = options = {}
    options['defaultextension'] = '.csv'
    options['filetypes'] = [('csv', '.csv')]
    options['initialdir'] = 'D:\\programmation\workspace\eclipse\maitrise\results'
    options['initialfile'] = "outdoor_B_matrix_emissions" + ".csv"
    options['parent'] = root
    options['title'] = "Select the outdoor emission matrix B, should have 2 lines and 4 columns befor values"
    file_path = tkFileDialog.askopenfilename(**file_opt)
    open_file = csv.reader(open(file_path,'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    for row in open_file:
        if first_row == 1:
            first_row += 1
            IO_sectors = row
            continue
        if first_row == 2:
            first_row = 0
            continue
        dict_data.setdefault(row[0], {})
        for i in range(len(row) - 4):
            if row[i + 4] == 0:
                dict_data[row[0]].setdefault(IO_sectors[i + 4] , [])
                continue
            else:
                dict_data[row[0]].setdefault(IO_sectors[i + 4] , [])
                dict_data[row[0]][IO_sectors[i + 4]].append([row[2], row[3], row[i + 4]])
    return dict_data

def import_usetox():
    import Tkinter, tkFileDialog
    import csv
    root= Tkinter.Tk()
    root.withdraw()
    file_opt = options = {}
    options['defaultextension'] = '.csv'
    options['filetypes'] = [('csv', '.csv')]
    options['initialdir'] = 'D:\\programmation\workspace\eclipse\maitrise\results'
    options['initialfile'] = "output_usetox" + ".csv"
    options['parent'] = root
    options['title'] = "Select the USEtox output file, it should be a copy-paste of usetox results sheet without the first row and column"
    file_path = tkFileDialog.askopenfilename(**file_opt)
    open_file = csv.reader(open(file_path,'rb'), delimiter=';')
    dict_data = {}
    first_row = 1
    multiples = []
    for row in open_file:
        if first_row < 5:
            first_row += 1
            continue
        if row[0] in dict_data:
            multiples.append(row[0])
        dict_data.setdefault(row[0], row)
    return [dict_data, multiples]

def convert_write_results_art2(path, time_tag):
    import csv
    open_file = csv.reader(open(path + "main_results_art2" + time_tag +  ".csv",'rb'), delimiter=';')
    with open(path + "main_results_art2_with_coma" + time_tag +  ".csv", 'wb') as final_file:
        writen_file = csv.writer(final_file, delimiter=';')
        writen_file.writerow(["CAS","Sector","Direct intake per make $","median","2.5 percentile","97.5 percentile","total intake per make $","median","2.5 percentile","97.5 percentile","total self intake per make $","median","2.5 percentile","97.5 percentile","direct cc per make $","median","2.5 percentile","97.5 percentile","total cc per make $","median","2.5 percentile","97.5 percentile","total self cc per make $","median","2.5 percentile","97.5 percentile","direct ncc per make $","median","2.5 percentile","97.5 percentile","total ncc per make $","median","2.5 percentile","97.5 percentile","total self ncc per make $","median","2.5 percentile","97.5 percentile","direct ci per make $","median","2.5 percentile","97.5 percentile","total ci per make $","median","2.5 percentile","97.5 percentile","total self ci per make $","median","2.5 percentile","97.5 percentile","direct nci per make $","median","2.5 percentile","97.5 percentile","total nci per make $","median","2.5 percentile","97.5 percentile","total self nci per make $","median","2.5 percentile","97.5 percentile","direct total impact per make $","median","2.5 percentile","97.5 percentile","total total impact per make $","median","2.5 percentile","97.5 percentile","total self impact per make $","median","2.5 percentile","97.5 percentile"])
        first_row = 1
        for row in open_file:
            if first_row == 1:
                first_row = 0
                continue
            writen_file.writerow([str(row[i]).replace(".",",") for i in range(len(row) - 1)])