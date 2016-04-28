'''THis code should provide a way to calculate the matrix necessary to use the 1st article CF with economic data
the global framework is Damage = [CF] x [[diag(hours)]] x [[[conversion NAICS-IO]] x [[diag(1/tot prod)]] x (I-A)^(-1) x [economic demand]
the current code will generate the matrix [[diag(hours)]] x [[[conversion NAICS-IO]] x [[diag(1/tot prod)]] x (I-A)^(-1)'''
import numpy as np
import datetime, csv, os, sys
from numpy.linalg import inv
from basic_functions import import_txt
time_stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
print "importing initial classification with hours"
original_classif_data = import_txt.import_csv("initial classification with labour hours for each sector, with one line header","original_structure",'.csv',[('csv', '.csv')])
first = 1
original_hours = {}
for line in original_classif_data[0]:
    if first == 1:
        first = 0
        continue
    original_hours[line[0]] = {'name' : line[1] , 'hours' : float(line[2])}
print "importing IO classification with total production value"
IO_classif_data = import_txt.import_csv("IO classification with total production value with one line header","io_structure",'.csv',[('csv', '.csv')])
first = 1
IO_prod = {}
for line in IO_classif_data[0]:
    if first == 1:
        first = 0
        continue
    IO_prod[line[0]] = {'name' : line[1] , 'tot_prod' : float(line[2]) , 'percent_urban' : float(line[3]) , 'super_sector' : line[4] , 'super_sector_name' : line[5]}

print "importing conversion matrix from initial classification to IO classification"
conversion_data = import_txt.import_csv("conversion matrix from initial classification to IO classification (lines: original, column: IO) with two lines and one column header","conversion_matrix",'.csv',[('csv', '.csv')])
count = 0
conversion_matrix = []
original_list = []
IO_list_conversion = []
for line in conversion_data[0]:
    if count == 0:
        count = 1
        continue
    if count == 1:
        size_IO = len(line) - 1
        for i in range(size_IO):
            IO_list_conversion.append(line[i + 1])
            if line[i + 1] not in IO_prod:
                print line[i + 1]
                print "IO sectors not corresponding in columns of conversion matrix"
                sys.exit(0)
        count = 2
        continue
    if line[0] not in original_hours:
        print "original sectors not corresponding in lines of conversion matrix"
        sys.exit(0)
    conversion_matrix.append([float(line[i + 1]) for i in range(size_IO)])
    original_list.append(line[0])
    count += 1
size_original = count - 2

print "importing matrix A"

A_matrix_data = import_txt.import_csv("economic IO A matrix with two lines and two columns header","A_matrix",'.csv',[('csv', '.csv')])
count = 0
A_matrix = []
IO_list_A_matrix_line = []
IO_list_A_matrix_column = []
for line in A_matrix_data[0]:
    if count == 0:
        if len(line) - 2 != size_IO:
            print "number of IO sectors not equal in A and conversion"
            sys.exit(0)
        for i in range(size_IO):
            IO_list_A_matrix_column.append(line[i + 2])
            if line[i + 2] not in IO_prod:
                print "IO sectors not corresponding in columns of A"
                sys.exit(0)
        count = 1
        continue
    if count == 1:
        count = 2
        continue
    if line[0] not in IO_prod:
        print "IO sectors not corresponding in lines of A"
        sys.exit(0)
    A_matrix.append([float(line[i + 2]) for i in range(size_IO)])
    IO_list_A_matrix_line.append(line[0])
    count += 1
if count - 2 != size_IO:
    print "original sectors not corresponding between hours and conversion matrix"
    sys.exit(0)

# we now check if the IO sectors order is the same for the conversion matrix columns and both lines and column from A matrix
print "checking sector order"
for i in range(size_IO):
    if IO_list_A_matrix_line[i] == IO_list_A_matrix_column[i] == IO_list_conversion[i]:
        continue
    else:
        print "IO sectors order not coherent"
        sys.exit(0)

# at this point the sectors are matching
#buidling hours and 1/tot prod matrixes
print "calculating matrices"
diag_h_matrix = np.matrix([[float(original_hours[original_list[i]]['hours']) if i == j else 0  for i in range(size_original)] for j in range(size_original)])
diag_inv_tot_prod_matrix = np.matrix([[float(1/IO_prod[IO_list_A_matrix_line[i]]['tot_prod']) if i == j and IO_prod[IO_list_A_matrix_line[i]]['tot_prod'] > 0 else 0  for i in range(size_IO)] for j in range(size_IO)])


I = np.matrix(np.eye(size_IO))
tot_inventory_generation_matrix = np.transpose(np.dot(diag_h_matrix,np.dot(np.matrix(conversion_matrix),np.dot(diag_inv_tot_prod_matrix,inv(I - np.matrix(A_matrix))))))
direct_inventory_generation_matrix = np.transpose(np.dot(diag_h_matrix,np.dot(np.matrix(conversion_matrix),diag_inv_tot_prod_matrix)))

#printing results in csv
print "exporting results"
with open(os.path.join('results_art_2','tot_inventory_generator_matrix_' + time_stamp + '.csv'), 'wb') as csvfile_1:
    with open(os.path.join('results_art_2','direct_inventory_generator_matrix_' + time_stamp + '.csv'), 'wb') as csvfile_2:
        writen_file_1 = csv.writer(csvfile_1, delimiter=';')
        writen_file_1.writerow([""] + [original_list[i] for i in range(size_original)])
        writen_file_2 = csv.writer(csvfile_2, delimiter=';')
        writen_file_2.writerow([""] + [original_list[i] for i in range(size_original)])
        for i in range(size_IO):
            line_direct = [IO_list_A_matrix_line[i]]
            line_tot = [IO_list_A_matrix_line[i]]
            for j in range(size_original):
                line_direct.append(str(direct_inventory_generation_matrix[i,j]).replace(".",","))
                line_tot.append(str(tot_inventory_generation_matrix[i,j]).replace(".",","))
            writen_file_1.writerow(line_tot)
            writen_file_2.writerow(line_direct)
