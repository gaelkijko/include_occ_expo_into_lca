'''THis code should provide a way to calculate the matrix necessary to use the 1st article CF with economic data
It is a correcte version that includes the use of the make matrix to convert the results to IO commodities as the IO model CEDA is provided on a commodityxcommodity basis.
the global framework is Damage = [CF] x [[diag(hours)]] x [[[conversion NAICS-IO]] x [[diag(1/tot_IO_sector_prod)]] x [[make_matrix]] x [[diag(1/tot_IO_commodity_prod)]] x (I-A)^(-1) x [economic demand]
the current code will generate the matrix [[diag(hours)]] x [[[conversion NAICS-IO]] x [[diag(1/tot_IO_sector_prod_from_make)]] x [[make_matrix]] x [[diag(1/tot_IO_commodity_prod_from_CEDA)]] x (I-A)^(-1)'''
import numpy as np
import datetime, csv, os, sys
from numpy.linalg import inv
from basic_functions import import_txt
time_stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')

print "importing initial classification with hours"
original_classif_data = import_txt.import_csv("initial classification with labour hours for each sector, with one line header","original_structure",'.csv',[('csv', '.csv')])
first = 1
original_hours_dict = {}
hours = []
hours_classif = []
for line in original_classif_data[0]:
    if first == 1:
        first = 0
        continue
    original_hours_dict[line[0]] = {'name' : line[1] , 'hours' : float(line[2])}
    hours.append(float(line[2]))
    hours_classif.append(line[0])

print "importing conversion matrix from initial classification to IO classification"
conversion_data = import_txt.import_csv("conversion matrix from initial classification to IO classification (lines: original, column: IO) with two lines and one column header","conversion_matrix",'.csv',[('csv', '.csv')])
count = 0
conversion_matrix = []
conversion_original_classif = []
conversion_IO_sectors_classif = []
size_IO_sector = 0
for line in conversion_data[0]:
    if count == 0:
        count = 1
        continue
    if count == 1:
        size_IO_sector = len(line) - 1
        for i in range(size_IO_sector):
            conversion_IO_sectors_classif.append(line[i + 1])
        count = 2
        continue
    conversion_matrix.append([float(line[i + 1]) for i in range(size_IO_sector)])
    conversion_original_classif.append(line[0])
    count += 1
size_original = count - 2

print "importing make matrix"
#rows are IO sectors, columns are IO commodities 
make_matrix_data = import_txt.import_csv("make matrixrows are IO sectors, columns are IO commodities with one lines and one column header","make_matrix",'.csv',[('csv', '.csv')])
make_matrix = []
make_IO_sect_classif = []
make_IO_com_classif = []
make_IO_sect_inv_tot_prod = []
vector = []
value = 0
first = 1
size_IO_commotity = 0
for line in make_matrix_data[0]:
    value = 0
    vector = []
    size_IO_commotity = len(line) - 1
    if first == 1:
        for i in range(size_IO_commotity):
            make_IO_com_classif.append(line[i +1])
        first = 0
        continue
    make_IO_sect_classif.append(line[0])
    vector = [float(line[i + 1]) for i in range(size_IO_commotity)]
    for i in range(len(vector)):
        value += vector[i]
    if value > 0:
        make_IO_sect_inv_tot_prod.append(float(1/value))
    else:
        make_IO_sect_inv_tot_prod.append(0)
    make_matrix.append(vector)


print "importing IO commodity classification with total commodity output from IO model"

IO_commodity_classif_data = import_txt.import_csv("IO commodity classification with total commodity output from IO model with one line header","io_commodity_structure",'.csv',[('csv', '.csv')])
first = 1
IO_commodity_dict = {}
IO_commodity_list = []
IO_commodity_inv_tot_output = []
for line in IO_commodity_classif_data[0]:
    if first == 1:
        first = 0
        continue
    IO_commodity_dict[line[0]] = {'name' : line[1] , 'tot_commodity_output' : line[2]}
    IO_commodity_list.append(line[0])
    if float(line[2]) > 0:
        IO_commodity_inv_tot_output.append(float(1/float(line[2])))
    else:
        IO_commodity_inv_tot_output.append(0)

print "importing matrix A"

A_matrix_data = import_txt.import_csv("economic IO A matrix with two lines and two columns header, commodity code in first","A_matrix",'.csv',[('csv', '.csv')])
count = 0
A_matrix = []
IO_list_A_matrix_line = []
IO_list_A_matrix_column = []
for line in A_matrix_data[0]:
    if count == 0:
        for i in range(size_IO_commotity):
            IO_list_A_matrix_column.append(line[i + 2])
        count = 1
        continue
    if count == 1:
        count = 2
        continue
    A_matrix.append([float(line[i + 2]) for i in range(size_IO_commotity)])
    IO_list_A_matrix_line.append(line[0])
    count += 1

# we now check if the IO sectors order is the same for the conversion matrix columns and both lines and column from A matrix
print "checking sector order"

for i in range(len(hours_classif)):
    if hours_classif[i] != conversion_original_classif[i]:
        print "hours classif and conversion original classif not matching"
        sys.exit(0)
for i in range(len(conversion_IO_sectors_classif)):
    if conversion_IO_sectors_classif[i] != make_IO_sect_classif[i]:
        print "conversion IO classif and make IO sector classif not matching"
        sys.exit(0)
for i in range(len(make_IO_com_classif)):
    if make_IO_com_classif[i] != IO_commodity_list[i]:
        print "make matrix IO commodity classif and IO commodity classif from IO model not matching"
        sys.exit(0)
    if IO_commodity_list[i] != IO_list_A_matrix_line[i]:
        print "IO commodity classif from IO model and A matrix line classif not matching"
        sys.exit(0)
    if IO_list_A_matrix_line[i] != IO_list_A_matrix_column[i]:
        print "A matrix line classif and A matrix column classif not matching"
        sys.exit(0)


# at this point the sectors are matching
#buidling hours and 1/tot prod matrixes

h_matrix = np.diag(hours)
inv_tot_sect_prod_matrix = np.diag(make_IO_sect_inv_tot_prod)
inv_tot_commodity_output_matrix = np.diag(IO_commodity_inv_tot_output)
I = np.matrix(np.eye(len(IO_commodity_inv_tot_output)))


print "calculating matrices"
print h_matrix.shape
print np.matrix(conversion_matrix).shape
direct_inventory_generation_matrix = np.dot(h_matrix,np.matrix(conversion_matrix))
print inv_tot_sect_prod_matrix.shape
direct_inventory_generation_matrix = np.dot(direct_inventory_generation_matrix,inv_tot_sect_prod_matrix)
print np.matrix(make_matrix).shape
direct_inventory_generation_matrix = np.dot(direct_inventory_generation_matrix,np.matrix(make_matrix))
print inv_tot_commodity_output_matrix.shape
direct_inventory_generation_matrix = np.dot(direct_inventory_generation_matrix,inv_tot_commodity_output_matrix)
print direct_inventory_generation_matrix.shape
direct_inventory_generation_matrix = direct_inventory_generation_matrix.T
print direct_inventory_generation_matrix.shape
tot_inventory_generation_matrix = np.dot(direct_inventory_generation_matrix.T,inv(I - np.matrix(A_matrix))).T


#printing results in csv
print "exporting results"
with open(os.path.join('results_art_2','tot_inventory_generator_matrix_' + time_stamp + '.csv'), 'wb') as csvfile_1:
    with open(os.path.join('results_art_2','direct_inventory_generator_matrix_' + time_stamp + '.csv'), 'wb') as csvfile_2:
        writen_file_1 = csv.writer(csvfile_1, delimiter=';')
        writen_file_1.writerow([""] + [hours_classif[i] for i in range(len(hours_classif))])
        writen_file_2 = csv.writer(csvfile_2, delimiter=';')
        writen_file_2.writerow([""] + [hours_classif[i] for i in range(len(hours_classif))])
        for i in range(len(make_IO_com_classif)):
            line_direct = [IO_list_A_matrix_line[i]]
            line_tot = [IO_list_A_matrix_line[i]]
            for j in range(len(hours_classif)):
                line_direct.append(str(direct_inventory_generation_matrix[i,j]).replace(".",","))
                line_tot.append(str(tot_inventory_generation_matrix[i,j]).replace(".",","))
            writen_file_1.writerow(line_tot)
            writen_file_2.writerow(line_direct)
