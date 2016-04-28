'''
Created on 27 janv. 2014

@author: Gael
'''
def import_csv(string_file_to_open,generic_file_name,default_extension,possible_extensions):
    import Tkinter, tkFileDialog
    import csv
    import os
    directory = os.pardir
    filename = os.path.join(directory,'maitrise', 'files_art2')
    root= Tkinter.Tk()
    root.withdraw()
    file_opt = options = {}
    options['defaultextension'] = default_extension
    options['filetypes'] = possible_extensions
    options['initialdir'] = filename
    options['initialfile'] = generic_file_name + '.csv'
    options['parent'] = root
    options['title'] = string_file_to_open
    file_path = tkFileDialog.askopenfilename(**file_opt)
    
    
    extracted = csv.reader(open(file_path,'rb'), delimiter=';')
    data_extracted = []
    for row in extracted:
        for i in range(len(row)):
            row[i]=row[i].replace(',','.')
            
        data_extracted.append(row)
    
    data=[data_extracted,len(data_extracted),len(data_extracted[0])]
    
    return data;