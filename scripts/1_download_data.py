# Script para download dos dados -----------------------------------------------

# Esse script irá usar as informações contidas no arquivo downloads.json para
# baixar os dados de imageamento estrutural (anatômico). Os primeiros arquivos
# referenciados no .json são arquivos de informação do dataset e são ignorados,
# e os arquivos com informações do dataset já estão na pasta ../data/.
# Vale observar que os dados de ressonância funcionais são ignorados.
# Esse script precisa ser executado apenas uma vez para obter todos os dados
# (se, no dia em que você executar, ainda estiverem disponíveis). O Download 
# contém aproximadamente 3Gb.

# Para executar esse script só é necessário atualizar a variável
# download_file_path. Essaa variável deve se referir ao arquivo json disponível
# no link: https://openneuro.org/crn/datasets/ds000115/snapshots/00001/download.
# Note que esse arquivo já está salvo neste git em ../data/download.json.


# Preâmbulo --------------------------------------------------------------------
import json
import urllib.request
import os

save_path          = '../data/anat/'
download_file_path = '../data/download.json'


# Função principal -------------------------------------------------------------
if __name__ == '__main__':

    if not os.path.exists(save_path):
        os.mkdir(save_path)
        
    with open(download_file_path, 'r') as f:
        datastore = json.loads(f.read())
        
        # queremos os dados de 3-699, apenas as imagens anatomicas
        for i in range(3, 700):
            filename = datastore['files'][i]['filename']
            
            # Pegando apenas os dados anatomicos
            if 'anat' in filename:
                
                # Evitar repetir o download
                if not os.path.exists( save_path + filename.replace('/', '_')):
                    url = datastore['files'][i]['urls'][0]

                    print('Downloading', filename, url)

                    urllib.request.urlretrieve(url, save_path + filename.replace('/', '_'))
                else:
                    print(filename, 'already downloaded')