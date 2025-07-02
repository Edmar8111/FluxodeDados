import os 
import subprocess
import shutil
from setuptools import setup
from Cython.Build import cythonize
from distutils.core import Extension
from time import sleep

path_exec='C:/Users/209/desktop/script-code/execBot/conf/gerenciamento'
arquivo_py="""
import os
import hashlib
def GerarKey(value):
    random_bytes=os.urandom(value)
    hash_object=hashlib.sha256(random_bytes)
    hash_digest=hash_object.hexdigest()
    return hash_digest
v=GerarKey(32)
"""

with open('generate.py', 'w') as file:
    file.write(arquivo_py)
sleep(1)
py_path=os.path.abspath('generate.py')

try:
    cmd_insert=["powershell",f"py -m nuitka --module {py_path} "]
    subprocess.run(cmd_insert, cwd=path_exec, shell=True, check=True)
    print('Arquivo Compilado')
except Exception as e:
    print(f'Erro ao gerar o arquivo .pyd {e}')


try:
    if os.path.isfile('C:/Users/209/desktop/script-code/execBot/conf/gerenciamento/generate.py'):
        os.remove('C:/Users/209/desktop/script-code/execBot/conf/gerenciamento/generate.py')
        print('Arquivo generate.py Deletado')
    if os.path.isfile('C:/Users/209/desktop/script-code/execBot/conf/gerenciamento/generate.pyi'):
        shutil.move('C:/Users/209/desktop/script-code/execBot/conf/gerenciamento/generate.cp312-win_amd64.pyd', 'C:/Users/209/desktop/script-code/execBot/conf/firewall')
        shutil.move('C:/Users/209/desktop/script-code/execBot/conf/gerenciamento/generate.build', 'C:/Users/209/desktop/script-code/execBot/conf/firewall')
        os.remove('C:/Users/209/desktop/script-code/execBot/conf/gerenciamento/generate.pyi')
        
        print('Arquivo movido')

except Exception as e:
    print(f'Error to validate pyd file {e}')
      