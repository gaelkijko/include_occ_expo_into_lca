import multiprocessing as mp
from multiprocessing.sharedctypes import Value
import ctypes
import datetime

#cumul function
def cumul(time_stp,nb_iter,IO_sector_list,task_for_cumul,kill_switch_cumul):
    import csv
    import os
    import numpy as np
    sector_data = {sector : [[float(0) for i in range(nb_iter + 1)] for j in range(10)] for sector in IO_sector_list}
    '''structure: sector_data = {sector : [
    0 ->direct_cc
    1 ->direct_ci
    2 ->tot_cc
    3 ->tot_ci
    4 ->direct_ncc
    5 ->direct_nci
    6 ->tot_ncc
    7 ->tot_nci
    8 ->direct_glob_i
    9 ->tot_glob_i ]}'''
    while kill_switch_cumul.value == 0 or task_for_cumul.qsize() > 0:
        try:
            data = task_for_cumul.get(timeout = 2)
        except:
            continue
        sector = data[0]
        if data[1] != 'Null':
            for i in range(4):
                for j in range(nb_iter + 1):
                    sector_data[sector][i][j] += data[1][i][j]
        if data[2] != 'Null':
            for i in range(4):
                for j in range(nb_iter + 1):
                    sector_data[sector][i + 4][j] += data[2][i][j]
    for sector in sector_data:
        for i in range(nb_iter + 1):
            sector_data[sector][8][i] = sector_data[sector][1][i] + sector_data[sector][5][i] #cumul for direct global impact
            sector_data[sector][9][i] = sector_data[sector][3][i] + sector_data[sector][7][i] #cumul for total global impact
    with open(os.path.join("results_art_2","IO_results",'IO_sector_data_boot_' + time_stp + '.csv'), 'ab') as csvfile_IO_sector_data_boot:
        with open(os.path.join("results_art_2","IO_results",'IO_sector_data_' + time_stp + '.csv'), 'ab') as csvfile_sector_data:
            writen_file_data_boot = csv.writer(csvfile_IO_sector_data_boot, delimiter=';')
            writen_file_data = csv.writer(csvfile_sector_data, delimiter=';')
            writen_file_data.writerow(['IO commodity','Direct Cancer Cases','Direct Cancer Cases median','Direct Cancer Cases 2.5 percentile','Direct Cancer Cases 97.5 percentile',
            'Direct Cancer Impact','Direct Cancer Impact median','Direct Cancer Impact 2.5 percentile','Direct Cancer Impact 97.5 percentile',
            'Total Cancer Cases','Total Cancer Cases median','Total Cancer Cases 2.5 percentile','Total Cancer Cases 97.5 percentile',
            'Total Cancer Impact','Total Cancer Impact median','Total Cancer Impact 2.5 percentile','Total Cancer Impact 97.5 percentile',
            'Direct Non Cancer Cases','Direct Non Cancer Cases median','Direct Non Cancer Cases 2.5 percentile','Direct Non Cancer Cases 97.5 percentile',
            'Direct Non Cancer Impact','Direct Non Cancer Impact median','Direct Non Cancer Impact 2.5 percentile','Direct Non Cancer Impact 97.5 percentile',
            'Total Non Cancer Cases','Total Non Cancer Cases median','Total Non Cancer Cases 2.5 percentile','Total Non Cancer Cases 97.5 percentile',
            'Total Non Cancer Impact','Total Non Cancer Impact median','Total Non Cancer Impact 2.5 percentile','Total Non Cancer Impact 97.5 percentile',
            'Direct Global Impact','Direct Global Impact median','Direct Global Impact 2.5 percentile','Direct Global Impact 97.5 percentile',
            'Total Global Impact','Total Global Impact median','Total Global Impact 2.5 percentile','Total Global Impact 97.5 percentile'])
            writen_file_data_boot.writerow(['IO sector','indicator','deterministic value'] + ['boot_' + str(i) for i in range(nb_iter)])
            for sector in sector_data:
                temp = []
                writen_file_data_boot.writerow([sector,'Direct Cancer Cases'] + [str('{:.4G}'.format(sector_data[sector][0][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Direct Cancer Impact'] + [str('{:.4G}'.format(sector_data[sector][1][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Total Cancer Cases'] + [str('{:.4G}'.format(sector_data[sector][2][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Total Cancer Impact'] + [str('{:.4G}'.format(sector_data[sector][3][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Direct Non Cancer Cases'] + [str('{:.4G}'.format(sector_data[sector][4][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Direct Non Cancer Impact'] + [str('{:.4G}'.format(sector_data[sector][5][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Total Non Cancer Cases'] + [str('{:.4G}'.format(sector_data[sector][6][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Total Non Cancer Impact'] + [str('{:.4G}'.format(sector_data[sector][7][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Direct Global Impact'] + [str('{:.4G}'.format(sector_data[sector][8][i])).replace('.',",") for i in range(nb_iter + 1)])
                writen_file_data_boot.writerow([sector,'Total Global Impact'] + [str('{:.4G}'.format(sector_data[sector][9][i])).replace('.',",") for i in range(nb_iter + 1)])
                temp += [sector,str('{:.4G}'.format(sector_data[sector][0][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][0][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][0][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][0][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][1][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][1][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][1][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][1][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][2][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][2][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][2][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][2][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][3][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][3][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][3][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][3][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][4][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][4][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][4][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][4][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][5][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][5][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][5][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][5][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][6][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][6][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][6][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][6][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][7][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][7][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][7][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][7][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][8][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][8][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][8][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][8][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                temp += [str('{:.4G}'.format(sector_data[sector][9][0])).replace('.',","),str('{:.4G}'.format(np.median([sector_data[sector][9][i + 1] for i in range(nb_iter)]))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][9][i + 1] for i in range(nb_iter)],2.5))).replace('.',","),str('{:.4G}'.format(np.percentile([sector_data[sector][9][i + 1] for i in range(nb_iter)],97.5))).replace('.',",")]
                writen_file_data.writerow(temp)

#processing function
def crunsher(original_sector_list,tasks_to_be_done,tasks_to_be_written,task_for_cumul,kill_switch_processing):
    import numpy as np
    import warnings
    warnings.simplefilter("error")
    while kill_switch_processing.value == 0 or tasks_to_be_done.qsize() > 0:
        try:
            data = tasks_to_be_done.get(timeout = 2)
        except:
            continue
        IO_sector_name = data[0]
        chem_name = data[1]
        IO_direct_inventory = np.array(data[2])
        IO_total_inventory = np.array(data[3])
        chem_data = data[4]
        breathing_rate = data[5]
        SF_non_cancer_data = data[6]
        SF_cancer_data = data[7]
        temp_direct_cc = []
        temp_direct_ncc = []
        temp_direct_ci = []
        temp_direct_nci = []
        temp_direct_ti = []
        temp_tot_cc = []
        temp_tot_ncc = []
        temp_tot_ci = []
        temp_tot_nci = []
        temp_tot_ti = []
        to_cumul = [IO_sector_name]
        to_write = [IO_sector_name,chem_name]
        nb_iter = len(SF_cancer_data) -1
        for i in range(nb_iter + 1): #for each bootstrap set and for the deterministic data we do the calculation
            conc_vector = np.array([chem_data['conc'][original_sector_list[j]][i] if original_sector_list[j] in chem_data['conc'] else float(0) for j in range(len(original_sector_list))])
            temp_direct_ti.append(0)
            temp_tot_ti.append(0)
            if chem_data['EF_cancer'] != 'Null':
                temp_direct_cc.append(np.dot(conc_vector,IO_direct_inventory) * breathing_rate * chem_data['EF_cancer'][i])
                temp_direct_ci.append(temp_direct_cc[i] * SF_cancer_data[i])
                temp_tot_cc.append(np.dot(conc_vector,IO_total_inventory) * breathing_rate * chem_data['EF_cancer'][i])
                temp_tot_ci.append(temp_tot_cc[i] * SF_cancer_data[i])
                temp_direct_ti[i] += temp_direct_ci[i]
                temp_tot_ti[i] += temp_tot_ci[i]
            if chem_data['EF_non_cancer'] != 'Null':
                temp_direct_ncc.append(np.dot(conc_vector,IO_direct_inventory) * breathing_rate * chem_data['EF_non_cancer'][i])
                temp_direct_nci.append(temp_direct_ncc[i] * SF_non_cancer_data[i])
                temp_tot_ncc.append(np.dot(conc_vector,IO_total_inventory) * breathing_rate * chem_data['EF_non_cancer'][i])
                temp_tot_nci.append(temp_tot_ncc[i] * SF_non_cancer_data[i])
                temp_direct_ti[i] += temp_direct_nci[i]
                temp_tot_ti[i] += temp_tot_nci[i]
        if chem_data['EF_cancer'] != 'Null':
            to_cumul.append([temp_direct_cc,temp_direct_ci,temp_tot_cc,temp_tot_ci])
            to_write.append([])
            to_write[2] += [temp_direct_cc[0],np.median([temp_direct_cc[j + 1] for j in range(nb_iter)]),np.percentile([temp_direct_cc[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_direct_cc[j + 1] for j in range(nb_iter)],97.5)]
            to_write[2] += [temp_direct_ci[0],np.median([temp_direct_ci[j + 1] for j in range(nb_iter)]),np.percentile([temp_direct_ci[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_direct_ci[j + 1] for j in range(nb_iter)],97.5)]
            to_write[2] += [temp_tot_cc[0],np.median([temp_tot_cc[j + 1] for j in range(nb_iter)]),np.percentile([temp_tot_cc[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_tot_cc[j + 1] for j in range(nb_iter)],97.5)]
            to_write[2] += [temp_tot_ci[0],np.median([temp_tot_ci[j + 1] for j in range(nb_iter)]),np.percentile([temp_tot_ci[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_tot_ci[j + 1] for j in range(nb_iter)],97.5)]
        else:
            to_cumul.append('Null')
            to_write.append('Null')
        if chem_data['EF_non_cancer'] != 'Null':
            to_cumul.append([temp_direct_ncc,temp_direct_nci,temp_tot_ncc,temp_tot_nci])
            to_write.append([])
            to_write[3] += [temp_direct_ncc[0],np.median([temp_direct_ncc[j + 1] for j in range(nb_iter)]),np.percentile([temp_direct_ncc[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_direct_ncc[j + 1] for j in range(nb_iter)],97.5)]
            to_write[3] += [temp_direct_nci[0],np.median([temp_direct_nci[j + 1] for j in range(nb_iter)]),np.percentile([temp_direct_nci[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_direct_nci[j + 1] for j in range(nb_iter)],97.5)]
            to_write[3] += [temp_tot_ncc[0],np.median([temp_tot_ncc[j + 1] for j in range(nb_iter)]),np.percentile([temp_tot_ncc[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_tot_ncc[j + 1] for j in range(nb_iter)],97.5)]
            to_write[3] += [temp_tot_nci[0],np.median([temp_tot_nci[j + 1] for j in range(nb_iter)]),np.percentile([temp_tot_nci[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_tot_nci[j + 1] for j in range(nb_iter)],97.5)]
        else:
            to_cumul.append('Null')
            to_write.append('Null')
        to_write.append([temp_direct_ti[0],np.median([temp_direct_ti[j + 1] for j in range(nb_iter)]),np.percentile([temp_direct_ti[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_direct_ti[j + 1] for j in range(nb_iter)],97.5),temp_tot_ti[0],np.median([temp_tot_ti[j + 1] for j in range(nb_iter)]),np.percentile([temp_tot_ti[j + 1] for j in range(nb_iter)],2.5),np.percentile([temp_tot_ti[j + 1] for j in range(nb_iter)],97.5)])
        tasks_to_be_written.put(to_write)
        task_for_cumul.put(to_cumul)


#writing function
def writing(tasks_to_be_written,kill_switch_writing,time_stp):
    import os
    import csv
    with open(os.path.join("results_art_2","IO_results",'IO_chem_couple_data_' + time_stp + '.csv'), 'ab') as csvfile_couple_data:
        writen_file = csv.writer(csvfile_couple_data, delimiter=';')
        writen_file.writerow(['IO commodity','CAS','Direct Cancer Cases','Direct Cancer Cases median','Direct Cancer Cases 2.5 percentile','Direct Cancer Cases 97.5 percentile',
        'Direct Cancer Impact','Direct Cancer Impact median','Direct Cancer Impact 2.5 percentile','Direct Cancer Impact 97.5 percentile',
        'Total Cancer Cases','Total Cancer Cases median','Total Cancer Cases 2.5 percentile','Total Cancer Cases 97.5 percentile',
        'Total Cancer Impact','Total Cancer Impact median','Total Cancer Impact 2.5 percentile','Total Cancer Impact 97.5 percentile',
        'Direct Non Cancer Cases','Direct Non Cancer Cases median','Direct Non Cancer Cases 2.5 percentile','Direct Non Cancer Cases 97.5 percentile',
        'Direct Non Cancer Impact','Direct Non Cancer Impact median','Direct Non Cancer Impact 2.5 percentile','Direct Non Cancer Impact 97.5 percentile',
        'Total Non Cancer Cases','Total Non Cancer Cases median','Total Non Cancer Cases 2.5 percentile','Total Non Cancer Cases 97.5 percentile',
        'Total Non Cancer Impact','Total Non Cancer Impact median','Total Non Cancer Impact 2.5 percentile','Total Non Cancer Impact 97.5 percentile',
        'Direct Global Impact','Direct Global Impact median','Direct Global Impact 2.5 percentile','Direct Global Impact 97.5 percentile',
        'Total Global Impact','Total Global Impact median','Total Global Impact 2.5 percentile','Total Global Impact 97.5 percentile'])
        while kill_switch_writing.value == 0 or tasks_to_be_written.qsize() > 0:
            try:
                data = tasks_to_be_written.get(timeout = 2)
            except:
                continue
            temp = [data[0], data[1],]
            if data[2] == 'Null':
                temp += [0 for i in range(16)]
            else:
                temp += ['{:.4G}'.format(data[2][i]).replace('.',",") for i in range(16)]
            if data[3] == 'Null':
                temp += [0 for i in range(16)]
            else:
                temp += ['{:.4G}'.format(data[3][i]).replace('.',",") for i in range(16)]
            temp += ['{:.4G}'.format(data[4][i]).replace('.',",") for i in range(8)]
            writen_file.writerow(temp)


# main function
if(__name__ == "__main__"):
    import os, csv, sys
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    import time
    #first we import concentration from article 1 script
    from basic_functions import import_txt
    print "importing article 1 bootstrap concentrations"
    bootstrap_concentration_article_1 = import_txt.import_csv("concentration file from article 1 script","hypothese_1_bootstrap_",'.csv',[('csv', '.csv')])
    #we create a dictionary of chemicals with sectors concentrations
    init_classif_conc_dict = {}
    first = 1 #this particular file has a header
    for line in bootstrap_concentration_article_1[0]: #line[0]: original sector, line[1]: CAS, other lines:bootstrap concentrations
        if first == 1:
            first = 0
            continue
        if len(line[0]) == 6: #we need to keep only concentrations for level 6
            all_null = 1
            for i in range(len(line)-2):
                if line[i]>0:
                    all_null = 0
                    break
            if all_null == 1: #case with all concentration being null
                continue
            else: #we populate the dictionary of initial concentrations, adding a 0 at the beginning for the "direct" concentration
                if line[1] in init_classif_conc_dict:
                    init_classif_conc_dict[line[1]]['conc'][line[0]] = [float(0)] + [float(line[i + 2]) / 1000000 for i in range(len(line) - 2)] #the 1/1000000 factor comes from the concentration imported in mg/m3 that we convert to kg/m3 to be coherent with EF data
                else:
                    init_classif_conc_dict[line[1]] = {'conc' : {line[0] : [float(0)] + [float(line[i + 2]) / 1000000 for i in range(len(line) - 2)]}}#the 1/1000000 factor comes from the concentration imported in mg/m3 that we convert to kg/m3 to be coherent with EF data
    bootstrap_concentration_article_1 = None
    #we now have to add the "direct concentrations from the main results of article 1 we will at the same time collect the hours worked by sectors at level 6 in the initial classification
    print "importing article 1 concentrations"
    main_results_article_1 = import_txt.import_csv("main results article 1","main_results",'.csv',[('csv', '.csv')])
    first = 1 #this particular file has a header
    for line in main_results_article_1[0]:
        if first == 1:
            first = 0
            continue
        if len(line[0]) == 6: #we need to keep only concentrastions for level 6
            if line[8] == 0 or line[8] == 'na':
                continue
            else: #we populate the dictionary of initial concentrations with the "direct" concentration
                if line[1] in init_classif_conc_dict:
                    init_classif_conc_dict[line[1]]['conc'][line[0]][0] = float(line[8]) / 1000000 #the 1/1000000 factor comes from the concentration imported in mg/m3 that we convert to kg/m3 to be coherent with EF data
                else:
                    print "error, positive direct concentration without bootstrap concentrations"
    main_results_article_1 = None
    
    #we now load the two inventory generating matrices (generated with the script generate_inventory_building_matrices
    
    tot_inventory_matrix_data = import_txt.import_csv("matrice de generation d'inventaire total","tot_inventory_generator_matrix_",'.csv',[('csv', '.csv')])
    direct_inventory_matrix_data = import_txt.import_csv("matrice de generation d'inventaire direct","direct_inventory_generator_matrix_",'.csv',[('csv', '.csv')])
    original_sector_list = [tot_inventory_matrix_data[0][0][i +1] for i in range(len(tot_inventory_matrix_data[0][0])-1)]
    IO_sectors_list = []
    tot_inventory_per_doll = {}
    direct_inventory_per_doll = {}
    size_IO = len(tot_inventory_matrix_data[0]) - 1
    size_original = len(tot_inventory_matrix_data[0][0]) - 1
    for i in range(size_IO):
        IO_sectors_list.append(tot_inventory_matrix_data[0][i + 1][0])
        all_null = 1
        temp = []
        for j in range(size_original):
            temp.append(float(tot_inventory_matrix_data[0][i + 1][j + 1]))
            if tot_inventory_matrix_data[0][i + 1][j + 1] > 0:
                all_null = 0
        if all_null == 1:
            temp = []
            continue
        else:
            tot_inventory_per_doll[tot_inventory_matrix_data[0][i + 1][0]] = temp
    
    for i in range(size_IO):
        all_null = 1
        temp = []
        for j in range(size_original):
            temp.append(float(direct_inventory_matrix_data[0][i + 1][j + 1]))
            if direct_inventory_matrix_data[0][i + 1][j + 1] > 0:
                all_null = 0
        if all_null == 1:
            temp = []
            continue
        else:
            direct_inventory_per_doll[direct_inventory_matrix_data[0][i + 1][0]] = temp
    temp = None
    all_null = None
    tot_inventory_matrix_data = None
    direct_inventory_matrix_data = None
    
    #we import EF and SF data from article 1 script
    all_EF_cancer_data = import_txt.import_csv("EF cancer data with bootstrap from article 1 script","EF_inh_cancer_bootstrap_",'.csv',[('csv', '.csv')])
    first = 1
    for i in range(len(all_EF_cancer_data[0])):
        temp = []
        all_null = 1
        if first == 1:
            first = 0
            continue
        temp.append(float(all_EF_cancer_data[0][i][1]))
        if all_EF_cancer_data[0][i][1] > 0:
            all_null = 0
        for j in range(all_EF_cancer_data[2] - 3):
            temp.append(float(all_EF_cancer_data[0][i][j + 3]))
            if temp[j + 1] > 0:
                all_null = 0
        if all_null == 1:
            if all_EF_cancer_data[0][i][0] in init_classif_conc_dict:
                init_classif_conc_dict[all_EF_cancer_data[0][i][0]]['EF_cancer'] = 'Null'
                continue
            else:
                continue
        else:
            init_classif_conc_dict[all_EF_cancer_data[0][i][0]]['EF_cancer'] = temp
    
    all_EF_non_cancer_data = import_txt.import_csv("EF non cancer data with bootstrap from article 1 script","EF_inh_non_cancer_bootstrap_",'.csv',[('csv', '.csv')])
    first = 1
    for i in range(len(all_EF_non_cancer_data[0])):
        temp = []
        all_null = 1
        if first == 1:
            first = 0
            continue
        temp.append(float(all_EF_non_cancer_data[0][i][1]))
        if all_EF_non_cancer_data[0][i][1] > 0:
            all_null = 0
        for j in range(all_EF_non_cancer_data[2] - 3):
            temp.append(float(all_EF_non_cancer_data[0][i][j + 3]))
            if temp[j + 1] > 0:
                all_null = 0
        if all_null == 1:
            if all_EF_non_cancer_data[0][i][0] in init_classif_conc_dict:
                init_classif_conc_dict[all_EF_non_cancer_data[0][i][0]]['EF_non_cancer'] = 'Null'
                continue
            else:
                continue
        else:
            init_classif_conc_dict[all_EF_non_cancer_data[0][i][0]]['EF_non_cancer'] = temp
    temp = None
    all_SF_data = import_txt.import_csv("SF data with bootstrap from article 1 script","severity_",'.csv',[('csv', '.csv')])
    first = 1
    temp_cancer = []
    temp_non_cancer = []
    for i in range(len(all_SF_data[0])):
        if first == 1:
            first = 0
            continue
        temp_cancer.append(float(all_SF_data[0][i][1]))
        temp_non_cancer.append(float(all_SF_data[0][i][2]))
    SF_cancer_data = temp_cancer
    SF_non_cancer_data = temp_non_cancer
    
    breathing_rate = float(1.6)
    
    #we create the queue for data processing
    tasks_to_be_done = mp.Queue() #we will fill this one in the main process
    tasks_to_be_written = mp.Queue() #we will fill this one in the processing childs
    task_for_cumul = mp.Queue() #we will fill this one in the writter child
    kill_switch_processing = Value(ctypes.c_int,0)
    kill_switch_writing = Value(ctypes.c_int,0)
    kill_switch_cumul = Value(ctypes.c_int,0)
    nb_cpu = mp.cpu_count()
    nb_iter = len(all_SF_data[0]) - 2
    
    #we start the processes so that they will start working while the queue is filled
    time_run = time.clock()
    print "starting processes"
    
    writer = mp.Process(target=writing, name = "writer_main", args = (tasks_to_be_written, kill_switch_writing, time_stamp))
    writer.start()
    
    cumulation = mp.Process(target=cumul, name = "cumul_main", args = (time_stamp,nb_iter,IO_sectors_list,task_for_cumul, kill_switch_cumul))
    cumulation.start()
    print nb_cpu
    for i in range(nb_cpu - 1):
        processor_child = mp.Process(target=crunsher, name = "processing_" + str(i), args= (original_sector_list,tasks_to_be_done,tasks_to_be_written,task_for_cumul,kill_switch_processing))
        processor_child.start()
    print str(nb_cpu) + " process started for main calculation with also 1 for cumul computation and 1 for writing in files"
    print "starting populating main queue"
    count_tasks = 0
    with open(os.path.join("results_art_2","IO_results",'IO_chem_couples_' + time_stamp + '.csv'), 'ab') as csvfile_couple_data:
        writen_file = csv.writer(csvfile_couple_data, delimiter=';')
        writen_file.writerow(['IO commodity','chem','direct inventory len','direct inventory sum','total inventory len','total inventory sum','initial classif with concentrations','nb EF cancer','nb EF non cancer','breathing rate','nb SF non cancer','nb SF cancer'])
        for IO_sector in IO_sectors_list:
            if IO_sector not in tot_inventory_per_doll: #case where the IO sector does not call any other sector
                continue
            for chem in init_classif_conc_dict:
                if init_classif_conc_dict[chem]['EF_cancer'] == init_classif_conc_dict[chem]['EF_non_cancer'] == 'Null': #case where the chemical does not have positive EF
                    continue
                else:
                    tasks_to_be_done.put([IO_sector,chem,direct_inventory_per_doll[IO_sector],tot_inventory_per_doll[IO_sector],init_classif_conc_dict[chem],breathing_rate,SF_non_cancer_data,SF_cancer_data])
                    count_tasks += 1
                    writen_file.writerow([IO_sector,chem,len(direct_inventory_per_doll[IO_sector]),sum(direct_inventory_per_doll[IO_sector]),len(tot_inventory_per_doll[IO_sector]),sum(tot_inventory_per_doll[IO_sector]),len(init_classif_conc_dict[chem]['conc']),len(init_classif_conc_dict[chem]['EF_cancer']),len(init_classif_conc_dict[chem]['EF_non_cancer']),breathing_rate,len(SF_non_cancer_data),len(SF_cancer_data)])
    print str(count_tasks) + " elements added to the main queue"
    while tasks_to_be_done.qsize() > 0:
        time_run = time.clock()
        print str(int(100 * (count_tasks - tasks_to_be_done.qsize()) / count_tasks))," % of main queue processed in ",int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth, ",tasks_to_be_done.qsize()," task to be done",tasks_to_be_written.qsize()," task to be written",task_for_cumul.qsize()," task to be cumulated"
        print mp.active_children() 
        time.sleep(5)
        continue
    kill_switch_processing.value = 1
    kill_switch_writing.value = 1
    kill_switch_cumul.value = 1
    time_run = time.clock()
    print "main queue processed in ",int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec and",int(1000*(time_run-int(time_run))),"thousandth"
    while  tasks_to_be_written.qsize() > 0 or task_for_cumul.qsize() > 0:
        time_run = time.clock()
        print "writing and aggregating results: ",str(int(100 * (count_tasks - tasks_to_be_written.qsize()) / count_tasks))," % results writene and ",str(int(100 * (count_tasks - task_for_cumul.qsize()) / count_tasks))," % results aggregated in ",int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
        time.sleep(5)
    while cumulation.is_alive():
        print "printing aggregated results"
    time_run = time.clock()
    print "calculation done in ",int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
        