import sys
import os
from time import sleep

if os.path.isfile('C:/Users/209/desktop/script-code/execBot/conf/firewall/generate.cp312-win_amd64.pyd'):
    print('Arquivos já inclusos')
else:
    import tokenCompiled
    tokenCompiled
    print('request')


sleep(5)
sys.path.append(r'C:\Users\209\desktop\script-code\execBot\conf\firewall')
import generate
print(generate.v)