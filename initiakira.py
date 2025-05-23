import os
import shutil

def returnCreateMove(pathDirectory, newFolder, folderFile, fileTOfind):
    pathDirectoryCreate=os.path.join(pathDirectory, newFolder)
    os.makedirs(pathDirectoryCreate, exist_ok=True)
    for a in os.listdir(folderFile):
        #efetua a localização do arquivo e move ele para a pasta especificada
        if a == fileTOfind:
            print(a)
            shutil.move(os.path.join(folderFile, a), os.path.join(pathDirectoryCreate, 'fileName.txt'))
    
    return print(f'Diretorio Base:{pathDirectory}, Diretorio criado:{newFolder}')
returnCreateMove('C:/Users/edmar/Desktop/Essencial_codes', 'teste', 'C:/Users/edmar/Desktop/Essencial_codes', 'test.html')