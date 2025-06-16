import os 
import shutil

class RequestFolder:
    def __init__(self, pathFolder, code, folderFind):
        """
        code=>Nome da pasta na qual contem os arquivos
        pathFolder=>Responsavel pelo traçamento da rota de destino de busca do diretorio
        folderFind=>A pasta na qual devera ser encontrada no diretorio e requisitado os dados
        """
        self.folder=None
        for i in os.listdir(f'{pathFolder}/{code} -'):
            if i==folderFind:
                self.folder=os.path.abspath(os.path.join(f'{pathFolder}/{code} -', i))
                break
        return None
    def copyFiles(self, moveFolder):
        self.folder=os.path.abspath(self.folder)
        print(self.folder)
        #efetua a alteração da copia para a pasta especificada obs: a pasta de destino deve estar no msm diretorio do codigo
        for i in os.listdir(self.folder):
            fileFolder=[a for a in os.listdir(os.path.abspath(moveFolder))]
            print(shutil.copy2(os.path.join(self.folder, i), os.path.abspath(moveFolder)) if i not in fileFolder else False)
        return 'File(s) Moved'
    
v=RequestFolder('C:/Users/edmar/Desktop/Essencial_codes/sdk', 0, 'nt').copyFiles('folder')
print(v)