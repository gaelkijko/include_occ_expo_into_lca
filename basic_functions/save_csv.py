def save_csv(data,nb_line_column_headers,column_headers,nb_column_line_headers,line_headers,string_name_file_to_save):
    import csv
    import numpy as np
    with open(string_name_file_to_save+'.csv', 'wb') as csvfile:
        writen_file = csv.writer(csvfile, delimiter=';')
        if nb_line_column_headers == 1:
            writen_file.writerow(["" for i in range(nb_column_line_headers)] + column_headers)
        else:
            for i in range(nb_line_column_headers):
                writen_file.writerow(["" for i in range(nb_column_line_headers)] + column_headers[i])
        if isinstance(data, np.ndarray):
            data_list = data.tolist()
        else:
            data_list=data
        data = None #variable not in use anymore
        data_list_len = len(data_list)
        data_list_len_0 = len(data_list[0])
        try:
            data_list_2 = [[str(data_list[i][j]) for j in range(data_list_len_0)] for i in range(data_list_len)]
            for i in range(len(data_list)):
                for j in range(data_list_len_0):
                    data_list_2[i][j] = data_list_2[i][j].replace('.',',')
            if not data_list_len == len(line_headers):
                print "headers count does not match the line number"
                quit()
            else:
                if nb_column_line_headers == 1:
                    for i in range(len(data_list_2)):
                        writen_file.writerow([line_headers[i]] + data_list_2[i])
                else:
                    for i in range(data_list_len):
                        writen_file.writerow([line_headers[i][j] for j in range(nb_column_line_headers)] + data_list_2[i])
        except:
            data_list_2 = [str(data_list[i]) for i in range(data_list_len)]
            for i in range(len(data_list_2)):
                data_list_2[i] = data_list_2[i].replace('.',',')
            if not data_list_len == len(line_headers):
                print "headers count does not match the line number"
                quit()
            else:
                if nb_column_line_headers == 1:
                    for i in range(len(data_list_2)):
                        writen_file.writerow([line_headers[i]] + [data_list_2[i]])
                else:
                    for i in range(data_list_len):
                        writen_file.writerow([line_headers[i][j] for j in range(nb_column_line_headers)] + [data_list_2[i]])
    
        
                
                
            
        