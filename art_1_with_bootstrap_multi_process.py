from basic_functions import import_excel_to_dict
import time
from random import randint
import random
import numpy
import csv
import datetime
import multiprocessing as mp
from multiprocessing.sharedctypes import Value
import ctypes
import os

    
#for each couple, calculation of the concentration based on measured concentration
#def main_funct(substance,thread_number, conc_base_1, hours_base_1, sectors_base_1, ED_50, severity, severity_btstrp, nb_iter_bootestrat, q, r_main, r_boot_h1, r_boot_h1_2, r_boot_h2, r_boot_h2_2, r_boot_EF):
def main_funct(substance,thread_number, conc_base_1, hours_base_1, sectors_base_1, ED_50, severity, severity_btstrp, nb_iter_bootestrat, q, r_main, r_boot_h1, r_boot_h2, r_boot_EF, r_boot_sector_store, r_boot_sector_store_2):
    #for substance in conc_base:
    #print "processing " + substance
    all_conc_chem = [{},{},{},{}]
    for sector in conc_base_1:
        sector = int(sector)
        concentration = 0
        total_weight = 0
        count_conc = 0
        count_pos_conc = 0
        for measurment in conc_base_1[sector]:
            total_weight += measurment["weight"]
            concentration += measurment["weight"] * measurment["concentration"]
            count_conc += 1
            if measurment["concentration"] > 0:
                count_pos_conc += 1
        concentration = concentration / total_weight
        if all_conc_chem[0].setdefault(int(sector), {}) == {}:
            all_conc_chem[0][sector]["NAICS"] = int(sector)
            all_conc_chem[0][sector]["CAS"] = substance
            all_conc_chem[0][sector]["main_concentration"] = concentration
            all_conc_chem[0][sector]["main_tot_weight"] = total_weight
            all_conc_chem[0][sector]["nb_conc"] = count_conc
            all_conc_chem[0][sector]["nb_positive_conc"] = count_pos_conc
        else:
            print "error detected, on 'all_conc' dictionary building"
            quit()
        for i in range(3):
            new_sector = int(sector / (10 ** (i+1)))
            if all_conc_chem[i+1].setdefault(int(sector / (10 ** (i+1))), {}) == {}:
                all_conc_chem[i+1][new_sector]["NAICS"] = int(sector / (10 ** (i+1)))
                all_conc_chem[i+1][new_sector]["CAS"] = substance
                all_conc_chem[i+1][new_sector]["main_concentration"] = concentration * hours_base_1[str(sector)]["hours"] / hours_base_1[str(int(sector / (10 ** (i+1))))]["hours"]
                if i == 0:
                    all_conc_chem[1][new_sector]["conc_hyp_2"] = concentration * hours_base_1[str(sector)]["hours"]
                    all_conc_chem[1][new_sector]["tot_hours_previous_level_with_conc"] = hours_base_1[str(sector)]["hours"]
                all_conc_chem[i+1][new_sector]["main_tot_weight"] = "na"
                all_conc_chem[i+1][new_sector]["nb_conc"] = count_conc
                all_conc_chem[i+1][new_sector]["nb_positive_conc"] = count_pos_conc
                for j in range(nb_iter_bootestrat):
                    all_conc_chem[i+1][new_sector]["boot_strap_conc_h1_" + str(j)] = 0
                    all_conc_chem[i+1][new_sector]["boot_strap_conc_h2_" + str(j)] = 0
            else:
                all_conc_chem[i+1][new_sector]["main_concentration"] += concentration * hours_base_1[str(sector)]["hours"] / hours_base_1[str(int(sector / (10 ** (i+1))))]["hours"]
                all_conc_chem[i+1][new_sector]["nb_conc"] += count_conc
                all_conc_chem[i+1][new_sector]["nb_positive_conc"] += count_pos_conc
                if i == 0:
                    all_conc_chem[i+1][new_sector]["conc_hyp_2"] += concentration * hours_base_1[str(sector)]["hours"]
                    all_conc_chem[1][new_sector]["tot_hours_previous_level_with_conc"] += hours_base_1[str(sector)]["hours"]
    
    #print "concentrations calculated----calculating bootstrapped concentrations at level 6 and higher"
    #time_run=time.clock()
    #print int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
    
    #bootstraping to generate a distribution of couple concentration based on measured concentrations
    
    for i in range(nb_iter_bootestrat):
        for sector in all_conc_chem[0]:
            concentration = 0
            total_weight = 0
            size = len(conc_base_1[sector])
            for j in range(size):
                total_weight += conc_base_1[sector][randint(0,size-1)]["weight"]
                concentration += conc_base_1[sector][randint(0,size-1)]["weight"] * conc_base_1[sector][randint(0,size-1)]["concentration"]
            concentration = concentration / total_weight
            all_conc_chem[0][sector]["boot_strap_conc_h1_" + str(i)] = concentration
            all_conc_chem[0][sector]["boot_strap_conc_h2_" + str(i)] = concentration
            for k in range(3):
                new_sector = int(conc_base_1[sector][0]["NAICS"] / (10 ** (k+1)))
                all_conc_chem[k+1][new_sector]["boot_strap_conc_h1_" + str(i)] += concentration * hours_base_1[str(sector)]["hours"] / hours_base_1[str(int(sector / (10 ** (k+1))))]["hours"]
                if k == 0:
                    all_conc_chem[1][new_sector]["boot_strap_conc_h2_" + str(i)] += concentration * hours_base_1[str(sector)]["hours"]
    
    
    #print "bootstrapped concentrations calculated----calculating concentrations for hypothesis 2 moving up from level 6"
    #time_run=time.clock()
    #print int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
    
    
    #calculation of hypothesis 2 concentrations
    for sector in all_conc_chem[0]: #we cover here level 6
        all_conc_chem[0][sector]["conc_hyp_2"] = all_conc_chem[0][sector]["main_concentration"]
    
    
    for i in range(2): #we cover there only level 5 and 4
        for sector in all_conc_chem[i + 1]:
            #calculate the concentration a current level
            all_conc_chem[i + 1][sector]["conc_hyp_2"] /= all_conc_chem[i + 1][sector]["tot_hours_previous_level_with_conc"]
            #adding the product of current level concentration times current level tot h to the direct upper level conc_hyp_2
            if all_conc_chem[i + 2][int(sector / 10)].setdefault("conc_hyp_2" , 0) == 0:
                all_conc_chem[i + 2][int(sector / 10)]["conc_hyp_2"] += all_conc_chem[i + 1][sector]["conc_hyp_2"] * hours_base_1[str(sector)]["hours"]
            else:
                all_conc_chem[i + 2][int(sector / 10)]["conc_hyp_2"] += all_conc_chem[i + 1][sector]["conc_hyp_2"] * hours_base_1[str(sector)]["hours"]
            #adding the current level total hours to the direct upper level tot_hours_previous_level_with_conc
            if all_conc_chem[i + 2][int(sector / 10)].setdefault("tot_hours_previous_level_with_conc" , 0) == 0:
                all_conc_chem[i + 2][int(sector / 10)]["tot_hours_previous_level_with_conc"] += hours_base_1[str(sector)]["hours"]
            else:
                all_conc_chem[i + 2][int(sector / 10)]["tot_hours_previous_level_with_conc"] += hours_base_1[str(sector)]["hours"]
            #doing the same for bootstrap concentrations
            for j in range(nb_iter_bootestrat):
                all_conc_chem[i + 1][sector]["boot_strap_conc_h2_" + str(j)] /= all_conc_chem[i + 1][sector]["tot_hours_previous_level_with_conc"]
                if all_conc_chem[i + 2][int(sector / 10)].setdefault("boot_strap_conc_h2_" + str(j) , 0) == 0:
                    all_conc_chem[i + 2][int(sector / 10)]["boot_strap_conc_h2_" + str(j)] += all_conc_chem[i + 1][sector]["boot_strap_conc_h2_" + str(j)] * hours_base_1[str(sector)]["hours"]
                else:
                    all_conc_chem[i + 2][int(sector / 10)]["boot_strap_conc_h2_" + str(j)] += all_conc_chem[i + 1][sector]["boot_strap_conc_h2_" + str(j)] * hours_base_1[str(sector)]["hours"]
                          
    for sector in all_conc_chem[3]: #we cover there level 3
        all_conc_chem[3][sector]["conc_hyp_2"] /= all_conc_chem[3][sector]["tot_hours_previous_level_with_conc"]
        for j in range(nb_iter_bootestrat):
            all_conc_chem[3][sector]["boot_strap_conc_h2_" + str(j)] /= all_conc_chem[3][sector]["tot_hours_previous_level_with_conc"]

    for i in range(3):
        sectors_list_lvl_tot = [int(a) for a in sectors_base_1 if sectors_base_1[a]["Digits"] == 4 + i]
        for sector in all_conc_chem[3 - i]:
            for possible_sector in [int(sub_sector) for sub_sector in sectors_list_lvl_tot if str(sub_sector).startswith(str(sector))]:
                try:
                    if all_conc_chem[2 - i].setdefault(possible_sector , {}) == {}:
                        all_conc_chem[2 - i][possible_sector]["main_concentration"] = "na"
                        all_conc_chem[2 - i][possible_sector]["conc_hyp_2"] = all_conc_chem[3 - i][sector]["conc_hyp_2"]
                        all_conc_chem[2 - i][possible_sector]["nb_conc"] = "0"
                        all_conc_chem[2 - i][possible_sector]["nb_positive_conc"] = "0"
                        all_conc_chem[2 - i][possible_sector]["main_tot_weight"] = "na"
                        all_conc_chem[2 - i][possible_sector]["CAS"] = substance
                        all_conc_chem[2 - i][possible_sector]["NAICS"] = possible_sector
                        for j in range(nb_iter_bootestrat):
                            all_conc_chem[2 - i][possible_sector]["boot_strap_conc_h2_" + str(j)] = all_conc_chem[3 - i][sector]["boot_strap_conc_h2_" + str(j)]
                            all_conc_chem[2 - i][possible_sector]["boot_strap_conc_h1_" + str(j)] = "na"   
                except:
                    continue
    
    #print "All concentrations calculated----calculating bootstrap distribution parameters"
    #time_run=time.clock()
    #print int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
    
    
    
    
    #calculation of couple concentration distribution parameters
    
    for j in range(4):
        for sector in all_conc_chem[j]:
            main_conc = all_conc_chem[j][sector]["main_concentration"]
            if main_conc == "na":
                all_conc_chem[j][sector]["boot_low_95_h1"] = "na"
                all_conc_chem[j][sector]["boot_high_95_h1"] = "na"
                all_conc_chem[j][sector]["boot_med_h1"] = "na"
                all_conc_chem[j][sector]["boot_low_95_h2"] = '{:.4G}'.format(numpy.percentile([all_conc_chem[j][sector]["boot_strap_conc_h2_" + str(i)] for i in range(nb_iter_bootestrat)], 2.5)).replace('.',",")
                all_conc_chem[j][sector]["boot_high_95_h2"] = '{:.4G}'.format(numpy.percentile([all_conc_chem[j][sector]["boot_strap_conc_h2_" + str(i)] for i in range(nb_iter_bootestrat)], 97.5)).replace('.',",")
                all_conc_chem[j][sector]["boot_med_h2"] = '{:.4G}'.format(numpy.median([all_conc_chem[j][sector]["boot_strap_conc_h2_" + str(i)] for i in range(nb_iter_bootestrat)])).replace('.',",")
            else:
                all_conc_chem[j][sector]["boot_low_95_h1"] = '{:.4G}'.format(numpy.percentile([all_conc_chem[j][sector]["boot_strap_conc_h1_" + str(i)] for i in range(nb_iter_bootestrat)], 2.5)).replace('.',",")
                all_conc_chem[j][sector]["boot_high_95_h1"] = '{:.4G}'.format(numpy.percentile([all_conc_chem[j][sector]["boot_strap_conc_h1_" + str(i)] for i in range(nb_iter_bootestrat)], 97.5)).replace('.',",")
                all_conc_chem[j][sector]["boot_med_h1"] = '{:.4G}'.format(numpy.median([all_conc_chem[j][sector]["boot_strap_conc_h1_" + str(i)] for i in range(nb_iter_bootestrat)])).replace('.',",")
                all_conc_chem[j][sector]["boot_low_95_h2"] = '{:.4G}'.format(numpy.percentile([all_conc_chem[j][sector]["boot_strap_conc_h2_" + str(i)] for i in range(nb_iter_bootestrat)], 2.5)).replace('.',",")
                all_conc_chem[j][sector]["boot_high_95_h2"] = '{:.4G}'.format(numpy.percentile([all_conc_chem[j][sector]["boot_strap_conc_h2_" + str(i)] for i in range(nb_iter_bootestrat)], 97.5)).replace('.',",")
                all_conc_chem[j][sector]["boot_med_h2"] = '{:.4G}'.format(numpy.median([all_conc_chem[j][sector]["boot_strap_conc_h2_" + str(i)] for i in range(nb_iter_bootestrat)])).replace('.',",")
    
    '''
    #saving as csv
    with open('main_results_' + time_stp + '.csv', 'ab') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        for i in range(4):
            for sector in all_conc_chem[i]:
                writen_file.writerow([sector,substance,all_conc_chem[i][sector]["main_concentration"],all_conc_chem[i][sector]["nb_conc"],all_conc_chem[i][sector]["conc_hyp_2"],all_conc_chem[i][sector]["main_tot_weight"],all_conc_chem[i][sector]["boot_med_h1"],all_conc_chem[i][sector]["boot_low_95_h1"],all_conc_chem[i][sector]["boot_high_95_h1"],all_conc_chem[i][sector]["boot_med_h2"],all_conc_chem[i][sector]["boot_low_95_h2"],all_conc_chem[i][sector]["boot_high_95_h2"]])
    with open('hypothese_1_bootstrap_' + time_stp + '.csv', 'ab') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        for i in range(4):
            for sector in all_conc_chem[i]:
                writen_file.writerow([sector,substance] + [all_conc_chem[i][sector]["boot_strap_conc_h1_" + str(j)] for j in range(nb_iter_bootestrat)])
    with open('hypothese_2_bootstrap_' + time_stp +  '.csv', 'ab') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        for i in range(4):
            for sector in all_conc_chem[i]:
                writen_file.writerow([sector,substance] + [all_conc_chem[i][sector]["boot_strap_conc_h2_" + str(j)] for j in range(nb_iter_bootestrat)])
    '''
    
    #construction of EF from ED50 USEtox
    
    if ED_50["ED_50_inh_canc_lifetime_kg"] == 0:
        EF_canc_inh = 0
    else:
        EF_canc_inh = 0.5 / ED_50["ED_50_inh_canc_lifetime_kg"]
    if ED_50["ED_50_inh_non_canc_lifetime_kg"] == 0:
        EF_non_canc_inh = 0
    else:
        EF_non_canc_inh = 0.5 / ED_50["ED_50_inh_non_canc_lifetime_kg"]
    Flag_canc_inh = ED_50["Flag_cancer_inh"]
    Flag_non_canc_inh = ED_50["Flag_non_cancer_inh"]
    if EF_canc_inh == 0:
        EF_canc_inh_boot = [0 for i in range(nb_iter_bootestrat)]
    else:
        EF_canc_inh_boot = [random.lognormvariate(numpy.log(EF_canc_inh), numpy.log(ED_50["GSD2_cancer"]) / 2) for i in range(nb_iter_bootestrat)]
    if EF_non_canc_inh == 0:
        EF_non_canc_inh_boot = [0 for i in range(nb_iter_bootestrat)]
    else:
        EF_non_canc_inh_boot = [random.lognormvariate(numpy.log(EF_non_canc_inh), numpy.log(ED_50["GSD2_non_cancer"]) / 2) for i in range(nb_iter_bootestrat)]
    
    #we print the EF via printer 1_1
    
    r_boot_EF.put([[substance,'{:.4G}'.format(EF_canc_inh).replace(".",","),Flag_canc_inh] + ['{:.4G}'.format(i).replace(".",",") for i in EF_canc_inh_boot],[substance,'{:.4G}'.format(EF_non_canc_inh).replace(".",","),Flag_non_canc_inh] + ['{:.4G}'.format(i).replace(".",",") for i in EF_non_canc_inh_boot]])
    
    #we then use the EF and severity data to calculate impact for all couples with uncertainty and send the corresponding lines to the queue for printing
    
    for i in range(4):
        for sector in all_conc_chem[i]:
            main_conc = all_conc_chem[i][int(sector)]["main_concentration"]
            inh_rate = sectors_base_1[str(sector)]["inhalation_rate"]
            conc_boot_h2 = [all_conc_chem[i][sector]["boot_strap_conc_h2_" + str(j)] for j in range(nb_iter_bootestrat)]
            canc_case_boot_h2 = [conc_boot_h2[j] * EF_canc_inh_boot[j] * inh_rate / 1000000 for j in range(nb_iter_bootestrat)]
            canc_case_boot_h2_indic = ['{:.4G}'.format(numpy.median(canc_case_boot_h2)).replace('.',","),'{:.4G}'.format(numpy.percentile(canc_case_boot_h2,2.5)).replace('.',","),'{:.4G}'.format(numpy.percentile(canc_case_boot_h2,97.5)).replace('.',",")]
            non_canc_case_boot_h2 = [conc_boot_h2[j] * EF_non_canc_inh_boot[j] * inh_rate / 1000000 for j in range(nb_iter_bootestrat)]
            non_canc_case_boot_h2_indic = ['{:.4G}'.format(numpy.median(non_canc_case_boot_h2)).replace('.',","),'{:.4G}'.format(numpy.percentile(non_canc_case_boot_h2,2.5)).replace('.',","),'{:.4G}'.format(numpy.percentile(non_canc_case_boot_h2,97.5)).replace('.',",")]
            canc_daly_boot_h2 = [canc_case_boot_h2[j] * severity_btstrp[j][0] for j in range(nb_iter_bootestrat)]
            canc_daly_boot_h2_indic = ['{:.4G}'.format(numpy.median(canc_daly_boot_h2)).replace('.',","),'{:.4G}'.format(numpy.percentile(canc_daly_boot_h2,2.5)).replace('.',","),'{:.4G}'.format( numpy.percentile(canc_daly_boot_h2,97.5)).replace('.',",")]
            non_canc_daly_boot_h2 = [non_canc_case_boot_h2[j] * severity_btstrp[j][1] for j in range(nb_iter_bootestrat)]
            non_canc_daly_boot_h2_indic = ['{:.4G}'.format(numpy.median(non_canc_daly_boot_h2)).replace('.',","),'{:.4G}'.format(numpy.percentile(non_canc_daly_boot_h2,2.5)).replace('.',","),'{:.4G}'.format( numpy.percentile(non_canc_daly_boot_h2,97.5)).replace('.',",")]
            tot_daly_boot_h2 = [canc_daly_boot_h2[j] + non_canc_daly_boot_h2[j] for j in range(nb_iter_bootestrat)]
            tot_daly_boot_h2_indic = ['{:.4G}'.format(numpy.median(tot_daly_boot_h2)).replace('.',","),'{:.4G}'.format(numpy.percentile(tot_daly_boot_h2,2.5)).replace('.',","),'{:.4G}'.format(numpy.percentile(tot_daly_boot_h2,97.5)).replace('.',",")]
            conc_h2 = all_conc_chem[i][sector]["conc_hyp_2"]
            h2_non_canc_case_temp = conc_h2 * EF_non_canc_inh * inh_rate / 1000000
            h2_canc_case_temp = conc_h2 * EF_canc_inh * inh_rate / 1000000
            h2_non_canc_daly_temp = h2_non_canc_case_temp * severity["non-cancer"]["Severity"]
            h2_canc_daly_temp = h2_canc_case_temp * severity["cancer"]["Severity"]
            
            h2_tot_daly = '{:.4G}'.format(h2_non_canc_daly_temp + h2_canc_daly_temp).replace('.',",")
            h2_canc_daly = '{:.4G}'.format(h2_canc_daly_temp).replace('.',",")
            h2_non_canc_daly = '{:.4G}'.format(h2_non_canc_daly_temp).replace('.',",")
            h2_canc_case = '{:.4G}'.format(h2_canc_case_temp).replace('.',",")
            h2_non_canc_case = '{:.4G}'.format(h2_non_canc_case_temp).replace('.',",")
            conc_h2 = '{:.4G}'.format(conc_h2).replace('.',",")
            if main_conc == "na":
                canc_case_boot_h1_indic = ["na", "na", "na"]
                non_canc_case_boot_h1_indic = ["na", "na", "na"]
                canc_daly_boot_h1_indic = ["na", "na", "na"]
                non_canc_daly_boot_h1_indic = ["na", "na", "na"]
                tot_daly_boot_h1_indic = ["na", "na", "na"]
                main_non_canc_case = "na"
                main_canc_case = "na"
                main_non_canc_daly = "na"
                main_canc_daly = "na"
                main_tot_daly = "na"
                main_intake = "na"
                r_boot_sector_store_2.put([sector,hours_base_1[str(sector)]["hours"],1 if Flag_canc_inh == "F" else 0,1 if Flag_non_canc_inh == "F" else 0, 0, 0,[h2_canc_case_temp , canc_case_boot_h2],[h2_non_canc_case_temp , non_canc_case_boot_h2],[h2_canc_daly_temp , canc_daly_boot_h2],[h2_non_canc_daly_temp , non_canc_daly_boot_h2]])
            else:
                main_intake = str(main_conc * inh_rate / 1000000).replace('.',",")
                #main_intake = '{:.4G}'.format(main_conc * inh_rate / 1000000).replace('.',",")
                conc_boot_h1 = [all_conc_chem[i][sector]["boot_strap_conc_h1_" + str(j)] for j in range(nb_iter_bootestrat)]
                canc_case_boot_h1 = [conc_boot_h1[j] * EF_canc_inh_boot[j] * inh_rate / 1000000 for j in range(nb_iter_bootestrat)]
                canc_case_boot_h1_indic = ['{:.4G}'.format(numpy.median(canc_case_boot_h1)).replace('.',","),'{:.4G}'.format(numpy.percentile(canc_case_boot_h1,2.5)).replace('.',","),'{:.4G}'.format( numpy.percentile(canc_case_boot_h1,97.5)).replace('.',",")]
                non_canc_case_boot_h1 = [conc_boot_h1[j] * EF_non_canc_inh_boot[j] * inh_rate / 1000000 for j in range(nb_iter_bootestrat)]
                non_canc_case_boot_h1_indic = ['{:.4G}'.format(numpy.median(non_canc_case_boot_h1)).replace('.',","),'{:.4G}'.format(numpy.percentile(non_canc_case_boot_h1,2.5)).replace('.',","),'{:.4G}'.format(numpy.percentile(non_canc_case_boot_h1,97.5)).replace('.',",")]
                canc_daly_boot_h1 = [canc_case_boot_h1[j] * severity_btstrp[j][0] for j in range(nb_iter_bootestrat)]
                canc_daly_boot_h1_indic = ['{:.4G}'.format(numpy.median(canc_daly_boot_h1)).replace('.',","),'{:.4G}'.format(numpy.percentile(canc_daly_boot_h1,2.5)).replace('.',","),'{:.4G}'.format(numpy.percentile(canc_daly_boot_h1,97.5)).replace('.',",")]
                non_canc_daly_boot_h1 = [non_canc_case_boot_h1[j] * severity_btstrp[j][1] for j in range(nb_iter_bootestrat)]
                non_canc_daly_boot_h1_indic = ['{:.4G}'.format(numpy.median(non_canc_daly_boot_h1)).replace('.',","),'{:.4G}'.format(numpy.percentile(non_canc_daly_boot_h1,2.5)).replace('.',","),'{:.4G}'.format( numpy.percentile(non_canc_daly_boot_h1,97.5)).replace('.',",")]
                tot_daly_boot_h1 = [canc_daly_boot_h1[j] + non_canc_daly_boot_h1[j] for j in range(nb_iter_bootestrat)]
                tot_daly_boot_h1_indic = ['{:.4G}'.format(numpy.median(tot_daly_boot_h1)).replace('.',","),'{:.4G}'.format(numpy.percentile(tot_daly_boot_h1,2.5)).replace('.',","),'{:.4G}'.format(numpy.percentile(tot_daly_boot_h1,97.5)).replace('.',",")]
        
                main_non_canc_case = main_conc * EF_non_canc_inh * inh_rate / 1000000
                main_canc_case = main_conc * EF_canc_inh * inh_rate / 1000000
                main_non_canc_daly = main_non_canc_case * severity["non-cancer"]["Severity"]
                main_canc_daly = main_canc_case * severity["cancer"]["Severity"] 
                main_tot_daly = '{:.4G}'.format(main_non_canc_daly + main_canc_daly).replace('.',",")
                #r_boot_h1.put([[sector,substance] + ['{:.4G}'.format(all_conc_chem[i][sector]["boot_strap_conc_h1_" + str(j)]).replace('.',",") for j in range(nb_iter_bootestrat)], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in canc_case_boot_h1], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in non_canc_case_boot_h1]])
                r_boot_h1.put([[sector,substance] + ['{:.4G}'.format(all_conc_chem[i][sector]["boot_strap_conc_h1_" + str(j)]).replace('.',",") for j in range(nb_iter_bootestrat)]])
                #r_boot_h1_2.put([[sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in canc_daly_boot_h1], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in non_canc_daly_boot_h1], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in tot_daly_boot_h1]])
                r_boot_sector_store.put([sector,hours_base_1[str(sector)]["hours"],1 if Flag_canc_inh == "F" else 0,1 if Flag_non_canc_inh == "F" else 0, all_conc_chem[i][sector]["nb_conc"], all_conc_chem[i][sector]["nb_positive_conc"],[main_canc_case,canc_case_boot_h1],[main_non_canc_case , non_canc_case_boot_h1],[main_canc_daly , canc_daly_boot_h1],[main_non_canc_daly , non_canc_daly_boot_h1]])
                r_boot_sector_store_2.put([sector,hours_base_1[str(sector)]["hours"],1 if Flag_canc_inh == "F" else 0,1 if Flag_non_canc_inh == "F" else 0, all_conc_chem[i][sector]["nb_conc"], all_conc_chem[i][sector]["nb_positive_conc"],[h2_canc_case_temp , canc_case_boot_h2],[h2_non_canc_case_temp , non_canc_case_boot_h2],[h2_canc_daly_temp , canc_daly_boot_h2],[h2_non_canc_daly_temp , non_canc_daly_boot_h2]])
                main_canc_case = '{:.4G}'.format(main_canc_case).replace('.',",")
                main_non_canc_case = '{:.4G}'.format(main_non_canc_case).replace('.',",")
                main_canc_daly = '{:.4G}'.format(main_canc_daly).replace('.',",")
                main_non_canc_daly = '{:.4G}'.format(main_non_canc_daly).replace('.',",")
                main_conc = str(main_conc).replace('.',",")
                #main_conc = '{:.4G}'.format(main_conc).replace('.',",")           
            r_main.put([sector,substance,int(hours_base_1[str(sector)]["hours"]), Flag_canc_inh, Flag_non_canc_inh, all_conc_chem[i][sector]["nb_conc"], all_conc_chem[i][sector]["nb_positive_conc"], str(all_conc_chem[i][sector]["main_tot_weight"]).replace('.',","), str(main_conc).replace('.',','), inh_rate, main_intake, all_conc_chem[i][sector]["boot_med_h1"],all_conc_chem[i][sector]["boot_low_95_h1"],all_conc_chem[i][sector]["boot_high_95_h1"], conc_h2,all_conc_chem[i][sector]["boot_med_h2"],all_conc_chem[i][sector]["boot_low_95_h2"],all_conc_chem[i][sector]["boot_high_95_h2"]] + [main_canc_case] + canc_case_boot_h1_indic + [h2_canc_case] + canc_case_boot_h2_indic + [main_non_canc_case] + non_canc_case_boot_h1_indic + [h2_non_canc_case] + non_canc_case_boot_h2_indic + [main_canc_daly] + canc_daly_boot_h1_indic + [h2_canc_daly] + canc_daly_boot_h2_indic + [main_non_canc_daly] + non_canc_daly_boot_h1_indic + [h2_non_canc_daly] + non_canc_daly_boot_h2_indic + [main_tot_daly] + tot_daly_boot_h1_indic + [h2_tot_daly] + tot_daly_boot_h2_indic)
            #r_boot_h2.put([[sector,substance] + ['{:.4G}'.format(all_conc_chem[i][sector]["boot_strap_conc_h2_" + str(j)]).replace('.',",") for j in range(nb_iter_bootestrat)], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in canc_case_boot_h2], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in non_canc_case_boot_h2]])
            r_boot_h2.put([[sector,substance] + ['{:.4G}'.format(all_conc_chem[i][sector]["boot_strap_conc_h2_" + str(j)]).replace('.',",") for j in range(nb_iter_bootestrat)]])
            #r_boot_h2_2.put([[sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in canc_daly_boot_h2], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in non_canc_daly_boot_h2], [sector,substance] + ['{:.4G}'.format(j).replace('.',",") for j in tot_daly_boot_h2]])
    q.put(thread_number)

def save_main(r_main, time_stp, kill_switch):
    with open(os.path.join("results_art1",'main_results_' + time_stp + '.csv'), 'ab') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        count = 0
        while True and count < 60:
            try:
                writen_file.writerow(r_main.get(timeout = 1))
                count = 0
            except:
                count += 1
            if kill_switch.value == 1:
                break

def boot_h1_save(r_boot_h1,time_stp, kill_switch):
    with open(os.path.join("results_art1",'hypothese_1_bootstrap_' + time_stp + '.csv'), 'ab') as csvfile:
        #with open(os.path.join("results",'hypothese_1_bootstrap_canc_cases_' + time_stp + '.csv'), 'ab') as csvfile_canc_cases:
        #with open(os.path.join("results",'hypothese_1_bootstrap_non_canc_cases_' + time_stp + '.csv'), 'ab') as csvfile_non_canc_cases:
        writen_file_0 = csv.writer(csvfile, delimiter=';')
        #writen_file_1 = csv.writer(csvfile_canc_cases, delimiter=';')
        #writen_file_2 = csv.writer(csvfile_non_canc_cases, delimiter=';')
        count = 0
        while True and count < 60:
            try:
                data = r_boot_h1.get(timeout = 1)
                count = 0
            except:
                count += 1
            if count == 0:
                writen_file_0.writerow(data[0])
                #writen_file_1.writerow(data[1])
                #writen_file_2.writerow(data[2])
            if kill_switch.value == 1:
                break

def boot_h1_save_2(r_boot_h1_2,time_stp, kill_switch):
    with open(os.path.join("results_art1",'hypothese_1_bootstrap_canc_daly_' + time_stp + '.csv'), 'ab') as csvfile_canc_daly:
        with open(os.path.join("results_art1",'hypothese_1_bootstrap_non_canc_daly_' + time_stp + '.csv'), 'ab') as csvfile_non_canc_daly:
            with open(os.path.join("results_art1",'hypothese_1_bootstrap_tot_daly_' + time_stp + '.csv'), 'ab') as csvfile_tot_daly:
                writen_file_3 = csv.writer(csvfile_canc_daly, delimiter=';')
                writen_file_4 = csv.writer(csvfile_non_canc_daly, delimiter=';')
                writen_file_5 = csv.writer(csvfile_tot_daly, delimiter=';')
                count = 0
                while True and count < 60:
                    try:
                        data = r_boot_h1_2.get(timeout = 1)
                        count = 0
                    except:
                        count += 1
                    if count == 0:
                        writen_file_3.writerow(data[0])
                        writen_file_4.writerow(data[1])
                        writen_file_5.writerow(data[2])
                    if kill_switch.value == 1:
                        break

def boot_h2_save(r_boot_h2,time_stp, kill_switch):
    with open(os.path.join("results_art1",'hypothese_2_bootstrap_' + time_stp + '.csv'), 'ab') as csvfile:
        #with open(os.path.join("results",'hypothese_2_bootstrap_canc_cases_' + time_stp + '.csv'), 'ab') as csvfile_canc_cases:
        #with open(os.path.join("results",'hypothese_2_bootstrap_non_canc_cases_' + time_stp + '.csv'), 'ab') as csvfile_non_canc_cases:
        writen_file_0 = csv.writer(csvfile, delimiter=';')
        #writen_file_1 = csv.writer(csvfile_canc_cases, delimiter=';')
        #writen_file_2 = csv.writer(csvfile_non_canc_cases, delimiter=';')
        count = 0
        while True and count < 60:
            try:
                data = r_boot_h2.get(timeout = 1)
                count = 0
            except:
                count += 1
            if count == 0:
                writen_file_0.writerow(data[0])
                #writen_file_1.writerow(data[1])
                #writen_file_2.writerow(data[2])
            if kill_switch.value == 1:
                break

def boot_h2_save_2 (r_boot_h2_2,time_stp, kill_switch):
    with open(os.path.join("results_art1",'hypothese_2_bootstrap_canc_daly_' + time_stp + '.csv'), 'ab') as csvfile_canc_daly:
        with open(os.path.join("results_art1",'hypothese_2_bootstrap_non_canc_daly_' + time_stp + '.csv'), 'ab') as csvfile_non_canc_daly:
            with open(os.path.join("results_art1",'hypothese_2_bootstrap_tot_daly_' + time_stp + '.csv'), 'ab') as csvfile_tot_daly:
                writen_file_3 = csv.writer(csvfile_canc_daly, delimiter=';')
                writen_file_4 = csv.writer(csvfile_non_canc_daly, delimiter=';')
                writen_file_5 = csv.writer(csvfile_tot_daly, delimiter=';')
                count = 0
                while True and count < 60:
                    try:
                        data = r_boot_h2_2.get(timeout = 1)
                        count = 0
                    except:
                        count += 1
                    if count == 0:
                        writen_file_3.writerow(data[0])
                        writen_file_4.writerow(data[1])
                        writen_file_5.writerow(data[2])
                    if kill_switch.value == 1:
                        break

def boot_EF (r_boot_EF,time_stp, kill_switch):
    with open(os.path.join("results_art1",'EF_inh_cancer_bootstrap_' + time_stp + '.csv'), 'ab') as csvfile_ef_canc:
        with open(os.path.join("results_art1",'EF_inh_non_cancer_bootstrap_' + time_stp + '.csv'), 'ab') as csvfile_ef_non_canc:
            writen_file_0 = csv.writer(csvfile_ef_canc, delimiter=';')
            writen_file_1 = csv.writer(csvfile_ef_non_canc, delimiter=';')
            count = 0
            while True and count < 60:
                try:
                    data = r_boot_EF.get(timeout = 1)
                    count = 0
                except:
                    count += 1
                if count == 0:
                    writen_file_0.writerow(data[0])
                    writen_file_1.writerow(data[1])
                if kill_switch.value == 1:
                    break


#def temp_reader (r_boot_sector,time_stp, kill_switch, r_boot_sector_store, r_boot_sector_store_2):
#    count = 0
#    while True and count < 30:
#        try:
#            data = r_boot_sector.get(timeout = 1)
#            count = 0
#        except:
#            count += 1
#        if count == 0:
#            r_boot_sector_store.put(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[10], data[11])
#            r_boot_sector_store_2.put(data[0], data[1], data[2], data[3], data[4], data[5], data[8], data[9], data[12], data[13])
#        if kill_switch.value == 1:
#            break
        
def sector_aggregator_2 (r_boot_sector_store_2,time_stp, kill_switch_2, nbre_iter_bootestrat, r_done): #dealing with only hyptohesis 2
    sectors_aggregated = {}
    count = 0
    nb_sector = 0
    while True and count < 60:
        try:
            line_temp = r_boot_sector_store_2.get(timeout = 2)
            count = 0
        except:
            count += 2
        if count == 0:
            if sectors_aggregated.setdefault(line_temp[0], []) == []:
                sectors_aggregated[line_temp[0]] = [line_temp[0], line_temp[1], 0, 0, 0, 0] + [[0, [0 for k in range(nbre_iter_bootestrat)]]for l in range(4)] #sector aggregated is : [sector,hours,flag canc, flag non canc, nb initial conc, nb positive initial conc , h2 cancer cases, h2 non cancer cases, h2 cancer daly, h2 non cancer daly] with each part (excetpt sector) comprisingh 2 items: the first being the main results, the other are the bootstrapped versions
                nb_sector += 1
            sectors_aggregated[line_temp[0]][2] += line_temp[2]
            sectors_aggregated[line_temp[0]][3] += line_temp[3]
            sectors_aggregated[line_temp[0]][4] += line_temp[4]
            sectors_aggregated[line_temp[0]][5] += line_temp[5]
            for i in range(4):
                if not len(line_temp[ i + 6]) == 0:
                    sectors_aggregated[line_temp[0]][i + 6][0] += line_temp[i + 6][0]           
                    for j in range(nbre_iter_bootestrat): 
                        sectors_aggregated[line_temp[0]][i + 6][1][j] += line_temp[i + 6][1][j]
        if kill_switch_2.value == 1:
            break
    with open(os.path.join("results_art1",'main_results_by_sectors_h2' + time_stp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["NAICS","Total hours","Flag EF cancer inhalation", "Flag EF non cancer inhalation", "Nb of measured concentrations", "Nb of positive measured concentration", "Cancer cases h2 per h", "Bootstrap h2 average cancer cases per h", "Bootstrap h2 cancer cases 2.5 percentile", "Bootstrap h2 cancer cases 97.5 percentile", "Non-cancer cases h2 per h", "Bootstrap h2 average non-cancer cases per h", "Bootstrap h2 non-cancer cases 2.5 percentile", "Bootstrap h2 non-cancer cases 97.5 percentile", "Cancer DALY h2 per h", "Bootstrap h2 average cancer DALY per h", "Bootstrap h2 cancer DALY 2.5 percentile", "Bootstrap h2 cancer DALY 97.5 percentile", "Non-cancer DALY h2 per h", "Bootstrap h2 average non-cancer DALY per h", "Bootstrap h2 non-cancer DALY 2.5 percentile", "Bootstrap h2 non-cancer DALY 97.5 percentile", "Total DALY h2 per h", "Bootstrap h2 average total DALY per h", "Bootstrap h2 total DALY 2.5 percentile", "Bootstrap h2 total DALY 97.5 percentile"])
        count = 0
        previous = ""
        for sector in sectors_aggregated:
            if sectors_aggregated[sector][2] > 0:
                sectors_aggregated[sector][2] = "F"
            else:
                sectors_aggregated[sector][2] = "not Flagged"
            if sectors_aggregated[sector][3] > 0:
                sectors_aggregated[sector][3] = "F"
            else:
                sectors_aggregated[sector][3] = "not Flagged"
            tot_h2 = [sectors_aggregated[sector][8][1][i] + sectors_aggregated[sector][9][1][i] for i in range(nbre_iter_bootestrat)]
            new_line_totd_h2 = ['{:.4G}'.format(sectors_aggregated[sector][8][0] + sectors_aggregated[sector][9][0]).replace(".", ","), '{:.4G}'.format(numpy.median(tot_h2)).replace(".", ","), '{:.4G}'.format(numpy.percentile(tot_h2,2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(tot_h2, 97.5)).replace(".", ",")]
            new_line_header = [sectors_aggregated[sector][0], sectors_aggregated[sector][1], sectors_aggregated[sector][2], sectors_aggregated[sector][3], sectors_aggregated[sector][4], sectors_aggregated[sector][5]]
            new_line_cc_h2 = ['{:.4G}'.format(sectors_aggregated[sector][6][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][6][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][6][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][6][1], 97.5)).replace(".", ",")]
            new_line_ncc_h2 = ['{:.4G}'.format(sectors_aggregated[sector][7][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][7][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][7][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][7][1], 97.5)).replace(".", ",")]
            new_line_cd_h2 = ['{:.4G}'.format(sectors_aggregated[sector][8][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][8][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][8][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][8][1], 97.5)).replace(".", ",")]
            new_line_ncd_h2 = ['{:.4G}'.format(sectors_aggregated[sector][9][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][9][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][9][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][9][1], 97.5)).replace(".", ",")]
            
            writen_file.writerow(new_line_header + new_line_cc_h2 + new_line_ncc_h2 + new_line_cd_h2 + new_line_ncd_h2 + new_line_totd_h2)
            sectors_aggregated[sector] = None
            count += 1
            if not str(int(100 * float(count) / float(nb_sector))) == previous:
                previous = str(int(100 * float(count) / float(nb_sector)))
                r_done.put(previous)

def sector_aggregator (r_boot_sector_store,time_stp, kill_switch_2, nbre_iter_bootestrat):
    sectors_aggregated = {}
    count = 0
    nb_sector = 0
    while True and count < 60:
        try:
            line_temp = r_boot_sector_store.get(timeout = 2)
            count = 0
        except:
            count += 2
        if count == 0:
            if sectors_aggregated.setdefault(line_temp[0], []) == []:
                sectors_aggregated[line_temp[0]] = [line_temp[0], line_temp[1], 0, 0, 0, 0] + [[0, [0 for k in range(nbre_iter_bootestrat)]]for l in range(4)] #sector aggregated is : [sector,hours,flag canc, flag non canc, nb initial conc, nb positive initial conc , h1 cancer cases, h1 non cancer cases, h2 cancer cases, h2 non cancer cases, h1 cancer daly, h1 non cancer daly, h2 cancer daly, h2 non cancer daly] with each part (excetpt sector) comprisingh 2 items: the first being the main results, the other are the bootstrapped versions
                nb_sector += 1
            sectors_aggregated[line_temp[0]][2] += line_temp[2]
            sectors_aggregated[line_temp[0]][3] += line_temp[3]
            sectors_aggregated[line_temp[0]][4] += line_temp[4]
            sectors_aggregated[line_temp[0]][5] += line_temp[5]
            for i in range(4):
                if not len(line_temp[i + 6]) == 0:
                    sectors_aggregated[line_temp[0]][i + 6][0] += line_temp[i + 6][0]          
                    for j in range(nbre_iter_bootestrat): 
                        sectors_aggregated[line_temp[0]][i + 6][1][j] += line_temp[i + 6][1][j]
            line_temp = None
        if kill_switch_2.value == 1:
            break
    with open(os.path.join("results_art1",'main_results_by_sectors_h1' + time_stp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["NAICS","Total hours","Flag EF cancer inhalation", "Flag EF non cancer inhalation", "Nb of measured concentrations", "Nb of positive measured concentration", "Cancer cases h1 per h", "Bootstrap h1 median cancer cases per h", "Bootstrap h1 cancer cases 2.5 percentile", "Bootstrap h1 cancer cases 97.5 percentile", "Non-cancer cases h1 per h", "Bootstrap h1 average non-cancer cases per h", "Bootstrap h1 non-cancer cases 2.5 percentile", "Bootstrap h1 non-cancer cases 97.5 percentile", "Cancer DALY h1 per h", "Bootstrap h1 average cancer DALY per h", "Bootstrap h1 cancer DALY 2.5 percentile", "Bootstrap h1 cancer DALY 97.5 percentile", "Non-cancer DALY h1 per h", "Bootstrap h1 average non-cancer DALY per h", "Bootstrap h1 non-cancer DALY 2.5 percentile", "Bootstrap h1 non-cancer DALY 97.5 percentile", "Total DALY h1 per h", "Bootstrap h1 average total DALY per h", "Bootstrap h1 total DALY 2.5 percentile", "Bootstrap h1 total DALY 97.5 percentile"])
        for sector in sectors_aggregated:
            if sectors_aggregated[sector][2] > 0:
                sectors_aggregated[sector][2] = "F"
            else:
                sectors_aggregated[sector][2] = "not Flagged"
            if sectors_aggregated[sector][3] > 0:
                sectors_aggregated[sector][3] = "F"
            else:
                sectors_aggregated[sector][3] = "not Flagged"
            tot_h1 = [sectors_aggregated[sector][8][1][i] + sectors_aggregated[sector][9][1][i] for i in range(nbre_iter_bootestrat)]
            new_line_header = [sectors_aggregated[sector][0], sectors_aggregated[sector][1], sectors_aggregated[sector][2], sectors_aggregated[sector][3], sectors_aggregated[sector][4], sectors_aggregated[sector][5]]
            new_line_totd_h1 = ['{:.4G}'.format(sectors_aggregated[sector][8][0] + sectors_aggregated[sector][9][0]).replace(".", ","), '{:.4G}'.format(numpy.median(tot_h1)).replace(".", ","), '{:.4G}'.format(numpy.percentile(tot_h1,2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(tot_h1, 97.5)).replace(".", ",")]
            new_line_cc_h1 = ['{:.4G}'.format(sectors_aggregated[sector][6][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][6][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][6][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][6][1], 97.5)).replace(".", ",")]
            new_line_ncc_h1 = ['{:.4G}'.format(sectors_aggregated[sector][7][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][7][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][7][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][7][1], 97.5)).replace(".", ",")]
            new_line_cd_h1 = ['{:.4G}'.format(sectors_aggregated[sector][8][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][8][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][8][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][8][1], 97.5)).replace(".", ",")]
            new_line_ncd_h1 = ['{:.4G}'.format(sectors_aggregated[sector][9][0]).replace(".", ","), '{:.4G}'.format(numpy.median(sectors_aggregated[sector][9][1])).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][9][1], 2.5)).replace(".", ","), '{:.4G}'.format(numpy.percentile(sectors_aggregated[sector][9][1], 97.5)).replace(".", ",")]
            
            writen_file.writerow(new_line_header + new_line_cc_h1 + new_line_ncc_h1 + new_line_cd_h1 + new_line_ncd_h1 + new_line_totd_h1)
            sectors_aggregated[sector] = None

if __name__ == '__main__':
    import sys
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    time_run=time.clock()
    q = mp.Queue()
    r_main = mp.Queue()
    r_boot_h1 = mp.Queue()
    #r_boot_h1_2 = mp.Queue()
    r_boot_h2 = mp.Queue()
    #r_boot_h2_2 = mp.Queue()
    r_boot_EF = mp.Queue()
    #r_boot_sector = mp.Queue()
    r_boot_sector_store = mp.Queue()
    r_boot_sector_store_2 = mp.Queue()
    r_done = mp.Queue()
    
    count_thread = 0
    done_thread = 0
    nb_cpu = mp.cpu_count()
    
    nbre_iter_bootestrat = 1000
    
    data_conc = import_excel_to_dict.import_conc_by_chem("Select the chemical database file","concentrations",'.xlsx',[('excel_new', '.xlsx')])
    data_hours= import_excel_to_dict.import_hours("Select the sector hours file","hours",'.xlsx',[('excel_new', '.xlsx')])
    data_sectors = import_excel_to_dict.import_sectors("Select the sector file","naics07",'.xlsx',[('excel_new', '.xlsx')])
    data_ED_50 = import_excel_to_dict.import_ED_50_by_CAS("Select the USEtox ED50 file","USEtox_ED50",'.xlsx',[('excel_new', '.xlsx')])
    data_severity = import_excel_to_dict.import_severity("Select the USEtox ED50 file","severity",'.xlsx',[('excel_new', '.xlsx')])
    
    #global conc_base
    conc_base=data_conc[0]
    nrow_base_conc=data_conc[1]
    ncol_base_conc=data_conc[2]
    
    #global hours_base
    hours_base=data_hours[0]
    nrow_base_hours=data_hours[1]
    ncol_base_hours=data_hours[2]
    
    #global sectors_base
    sectors_base=data_sectors[0]
    nrow_base_sectors=data_sectors[1]
    ncol_base_sectors=data_sectors[2]
    
    #global ED_50 base
    ED_50_base = data_ED_50[0]
    nrow_ED_50_base = data_ED_50[1]
    ncol_ED_50_base = data_ED_50[2]
    
    #global severity base
    severity_base = data_severity[0]
    
    print severity_base
    sys.exit()
    
    
    try:
        os.mkdir("results_art1")
    except Exception:
        pass
    
    #generation of severity for the bootstrap (the everity is not specific to a chemical, therefore it must be the same for all chemicals
    severity_bootstrap = [[random.lognormvariate(numpy.log(severity_base["cancer"]["Severity"]), numpy.log(severity_base["cancer"]["GSD2"]) / 2),random.lognormvariate(numpy.log(severity_base["non-cancer"]["Severity"]), numpy.log(severity_base["non-cancer"]["GSD2"]) / 2)] for i in range(nbre_iter_bootestrat)]
    
    with open(os.path.join("results_art1",'severity_' + time_stamp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["Case","Cancer Severity","Non-cancer Severity"])
        writen_file.writerow(["main",11.5,2.7])
        compteur = 1
        for i in severity_bootstrap:
            writen_file.writerow(["boot_" + str(compteur),i[0],i[1]])
            compteur += 1
    
    nb_tot_chem =sum([1 for substance in conc_base])
    done = 0
    
    print "base imported"
    time_run=time.clock()
    print int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
    
    first_chem = 0
    

    with open(os.path.join("results_art1",'main_results_' + time_stamp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["NAICS","CAS","Total hours","Flag EF cancer inhalation", "Flag EF non cancer inhalation", "Nb of measured concentrations", "Nb of positive measured concentration", "Total weight", "Concentration, mg/m3", "Breathing rate", "Intake per hour, kg/h", "Bootstrap average concentration h1","Bootstrap 2.5 percentile h1","Bootstrap 97.5 percentile h1", "Concentration h2","Bootstrap average concentration h2","Bootstrap 2.5 percentile h2","Bootstrap 97.5 percentile h2", "Cancer cases h1", "Bootstrap h1 average cancer cases ", "Bootstrap h1 cancer cases 2.5 percentile", "Bootstrap h1 cancer cases 97.5 percentile", "Cancer cases h2", "Bootstrap h2 average cancer cases ", "Bootstrap h2 cancer cases 2.5 percentile", "Bootstrap h2 cancer cases 97.5 percentile", "Non-cancer cases h1", "Bootstrap h1 average non-cancer cases ", "Bootstrap h1 non-cancer cases 2.5 percentile", "Bootstrap h1 non-cancer cases 97.5 percentile", "Non-cancer cases h2", "Bootstrap h2 average non-cancer cases ", "Bootstrap h2 non-cancer cases 2.5 percentile", "Bootstrap h2 non-cancer cases 97.5 percentile", "Cancer DALY h1", "Bootstrap h1 average cancer DALY ", "Bootstrap h1 cancer DALY 2.5 percentile", "Bootstrap h1 cancer DALY 97.5 percentile", "Cancer DALY h2", "Bootstrap h2 average cancer DALY ", "Bootstrap h2 cancer DALY 2.5 percentile", "Bootstrap h2 cancer DALY 97.5 percentile", "Non-cancer DALY h1", "Bootstrap h1 average non-cancer DALY ", "Bootstrap h1 non-cancer DALY 2.5 percentile", "Bootstrap h1 non-cancer DALY 97.5 percentile", "Non-cancer DALY h2", "Bootstrap h2 average non-cancer DALY ", "Bootstrap h2 non-cancer DALY 2.5 percentile", "Bootstrap h2 non-cancer DALY 97.5 percentile", "Total DALY h1", "Bootstrap h1 average total DALY", "Bootstrap h1 total DALY 2.5 percentile", "Bootstrap h1 total DALY 97.5 percentile", "Total DALY h2", "Bootstrap h2 average total DALY", "Bootstrap h2 total DALY 2.5 percentile", "Bootstrap h2 total DALY 97.5 percentile"])
    with open(os.path.join("results_art1",'hypothese_1_bootstrap_' + time_stamp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h1 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    with open(os.path.join("results_art1",'hypothese_2_bootstrap_' + time_stamp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h2 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    with open(os.path.join("results_art1",'EF_inh_cancer_bootstrap_' + time_stamp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["CAS", "Main EF inh cancer (cases/kg intake)", "Flag"] + ["Bootstrap EF inh cancer " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    with open(os.path.join("results_art1",'EF_inh_non_cancer_bootstrap_' + time_stamp + '.csv'), 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        writen_file.writerow(["CAS", "Main EF inh non cancer (cases/kg intake)", "Flag"] + ["Bootstrap EF inh non cancer " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_1_bootstrap_canc_cases_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h1 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_2_bootstrap_canc_cases_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h2 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_1_bootstrap_non_canc_cases_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h1 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_2_bootstrap_non_canc_cases_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h2 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_1_bootstrap_canc_daly_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h1 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_2_bootstrap_canc_daly_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h2 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_1_bootstrap_non_canc_daly_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h1 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_2_bootstrap_non_canc_daly_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h2 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_1_bootstrap_tot_daly_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h1 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    #with open(os.path.join("results",'hypothese_2_bootstrap_tot_daly_' + time_stamp + '.csv'), 'wb') as csvfile:
    #    writen_file = csv.writer(csvfile, delimiter=';')
    #    writen_file.writerow(["NAICS","CAS"] + ["Bootstrap concentration h2 " + str(i + 1) for i in range(nbre_iter_bootestrat)])
    
    kill_switch = Value(ctypes.c_int,0)
    kill_switch_2 = Value(ctypes.c_int,0)
    
    t_0 = mp.Process(target=save_main, name = "writer_main", args = (r_main, time_stamp, kill_switch))
    t_0.start()
    t_1 = mp.Process(target=boot_h1_save, name = "writer_h1_1", args = (r_boot_h1, time_stamp, kill_switch))
    t_1.start()
    #t = mp.Process(target=boot_h1_save_2, name = "writer_h1_2", args = (r_boot_h1_2, time_stamp, kill_switch))
    #t.start()
    t_2 = mp.Process(target=boot_h2_save, name = "writer_h2_1", args = (r_boot_h2, time_stamp, kill_switch))
    t_2.start()
    #t = mp.Process(target=boot_h2_save_2, name = "writer_h2_2", args = (r_boot_h2_2, time_stamp, kill_switch))
    #t.start()
    t_3 = mp.Process(target=boot_EF, name = "writer_EF", args = (r_boot_EF, time_stamp, kill_switch))
    t_3.start()
    t_4 = mp.Process(target=sector_aggregator, name = "sector_aggregator", args = (r_boot_sector_store,time_stamp, kill_switch_2, nbre_iter_bootestrat))
    t_4.start()
    #t = mp.Process(target=temp_reader, name = "temp_reader", args = (r_boot_sector,time_stamp, kill_switch, r_boot_sector_store))
    #t.start()
    t_5 = mp.Process(target=sector_aggregator_2, name = "sector_aggregator_2", args = (r_boot_sector_store_2,time_stamp, kill_switch_2, nbre_iter_bootestrat, r_done))
    t_5.start()
    
    correctif = 0
    
    
    for substance in conc_base:
        while True:
            if len(mp.active_children()) > nb_cpu + 5 + correctif:
                while len(mp.active_children()) > nb_cpu + 5 + correctif:
                    #print str(r_main.qsize()), str(r_boot_h1.qsize()), str(r_boot_h2.qsize()), str(r_boot_EF.qsize()), str(r_boot_sector_store.qsize()), str(r_boot_sector_store_2.qsize())
                    s = q.get(block = True)
                    done_thread += 1
                print "done " + str(float(int((10000 * done_thread) / nb_tot_chem)) / 100) + "%"
                time_run=time.clock()
                print int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
            else:
                #t = mp.Process(target=main_funct, name = "worker_" + substance + "_" + str(count_thread) , args = (substance,count_thread, conc_base[substance], hours_base, sectors_base, ED_50_base[substance], severity_base, severity_bootstrap, nbre_iter_bootestrat, q,  r_main, r_boot_h1, r_boot_h1_2, r_boot_h2, r_boot_h2_2, r_boot_EF))
                t = mp.Process(target=main_funct, name = "worker_" + substance + "_" + str(count_thread) , args = (substance,count_thread, conc_base[substance], hours_base, sectors_base, ED_50_base[substance], severity_base, severity_bootstrap, nbre_iter_bootestrat, q,  r_main, r_boot_h1, r_boot_h2, r_boot_EF, r_boot_sector_store, r_boot_sector_store_2))
                t.start()
                print "started " + substance
                count_thread += 1
                #print str(r_main.qsize()), str(r_boot_h1.qsize()), str(r_boot_h2.qsize()), str(r_boot_EF.qsize()), str(r_boot_sector_store.qsize()), str(r_boot_sector_store_2.qsize())
                break
    
    while not done_thread == nb_tot_chem:
        s = q.get()
        done_thread += 1
        print "done " + str(float(int((10000 * done_thread) / nb_tot_chem)) / 100) + "%"
        time_run=time.clock()
        print int(time_run/60),"min",int(time_run)-60*int(time_run/60),"sec",int(1000*(time_run-int(time_run))),"thousandth"
    
    while True:
        #if r_main.qsize() == 0 and r_boot_h1.qsize() == 0 and r_boot_h2.qsize() == 0 and r_boot_h1_2.qsize() == 0 and r_boot_h2_2.qsize() == 0:
        if r_main.qsize() == 0 and r_boot_h1.qsize() == 0 and r_boot_h2.qsize() == 0 and r_boot_EF.qsize() == 0:
            kill_switch.value += 1
            print "processes killed"
            break
        else:
            print "still printing "
            print "writer 1: " + str(r_main.qsize())
            print "writer 2: " + str(r_boot_h1.qsize())
            print "writer 3: " + str(r_boot_h2.qsize())
            print "writer 4: " + str(r_boot_EF.qsize() * 2)
            print "line to read: " + str(r_boot_sector_store_2.qsize())
            #print "writer 4: " + str(r_boot_h1_2.qsize() * 3)
            #print "writer 5: " + str(r_boot_h2_2.qsize() * 3)
            time.sleep(5)
    while  r_boot_sector_store_2.qsize() > 0 and r_boot_sector_store.qsize() > 0:
        print "aggregating sectors, " + str(r_boot_sector_store.qsize() + r_boot_sector_store_2.qsize()) + " lines remaining"
        time.sleep(2)
    kill_switch_2.value += 1
    print "still " + str(len(mp.active_children())) + " active child processes"
    count = 0
    while t_5.is_alive():
        try:
            data = r_done.get(timeout = 1)
            count = 0
        except:
            count += 1
        if count == 0:
            print "printing sectors to csv, " + data + "% done"



    
