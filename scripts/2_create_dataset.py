# Script para criação do dataset -----------------------------------------------

# Esse script deve ser executado após o 1_download_data.py. Ele irá aplicar o
# pré-processamento apresentado no notebook em docs/ para todos os arquivos que
# foram baixados, e então criar um arquivo .csv com as informações para cada
# sujeito. A ideia é utilizar os resultados do processo de visão computacional
# em modelos de aprendizado de máquina para a tarefa de classificação.

# É crucial para o funcionamento desse script que a variável data_path aponte
# para um diretório que contenha os seguintes arquivos/sub-diretórios:
# - anat/ - com os dados nii.gz baixados pelo script 1_download_data.py
# - gifs/ - pasta vazia para que esse script salve gifs processados
# - participants.csv - para que o script pegue informações dos participantes

# O script irá criar gifs em gifs/, que podem ser utilizados para visualizar
# as modificações que você pode fazer no pré processamento. Além disso, será
# criado um arquivo processed.csv com os resultados após aplicar a pipeline em
# cada indivíduo em anat/. As funções aqui estão sem comentários pois são
# apresentadas no notebook de pré processamento com mais detalhes.

# Como esse processamento é longo, o script pode ser interrompido e irá retomar
# de onde parou baseando-se no arquivo csv. O script já faz o tratamento para
# os dados que não consegue processar


# Preâmbulo --------------------------------------------------------------------
from nilearn           import datasets
from nilearn           import plotting
from deepbrain         import Extractor
from skimage.external  import tifffile as tif
from skimage.transform import resize
from scipy.signal      import find_peaks, medfilt
from scipy             import ndimage

import pandas            as pd
import nibabel           as nib
import numpy             as np
import matplotlib.pyplot as plt

import glob
import os
import PIL
import imageio
import cv2

plt.rcParams.update({'font.size': 18})

data_path = '../data/'


# Funções auxiliares -----------------------------------------------------------
def load_nii(path_file):
    
    img_raw = nib.load(path_file).get_fdata()
    
    img_np  = ndimage.rotate(img_raw, 90, axes=(0, 2), reshape=False)
    img_np  = 255*(img_np - np.min(img_np))/np.ptp(img_np)

    return img_np, img_raw


def _get_minmax(img, axis=0):

    axis_lens = [len(img[:, 0, 0]), len(img[0, :, 0]), len(img[0, 0, :])]
    all_axis  = [0, 1, 2]
    
    a_min, a_max = np.inf, 0

    a_len = axis_lens[axis]
    all_axis.remove(axis)

    b_len, c_len = axis_lens[all_axis[0]], axis_lens[all_axis[1]]

    for a in range(a_len):

        is_null = True

        for b in range(b_len):
            for c in range(c_len):
                if axis==0:
                    if img[a, b, c]>0:
                        is_null = False
                elif axis==1:
                    if img[b, a, c]>0:
                        is_null = False
                elif axis==2:
                    if img[b, c, a]>0:
                        is_null = False

        if not is_null:
            a_min = min(a_min, a)
            a_max = max(a_max, a)

    return a_min, a_max


def _get_edges(img):

    x_min, x_max = _get_minmax(img, axis=0)
    y_min, y_max = _get_minmax(img, axis=1)
    z_min, z_max = _get_minmax(img, axis=2)
    
    return x_min, x_max, y_min, y_max, z_min, z_max


def cut_on_edges(img):
    
    x_min, x_max, y_min, y_max, z_min, z_max = _get_edges(img)
    
    new_img = np.zeros( (x_max - x_min, y_max - y_min, z_max - z_min) )
    
    for x in range(x_max - x_min):
        for y in range(y_max - y_min):
            for z in range(z_max - z_min):
                new_img[x, y, z] = img[x_min + x, y_min + y, z_min + z]

    return new_img.astype('uint8')


def create_gif(sub, sub_white, sub_gray, sub_csf, fname='data', duration=0.05):
    
    min_size = np.min([s.shape for s in [sub, sub_white, sub_gray, sub_csf]])
    subs = []
    
    for s in [sub, sub_white, sub_gray, sub_csf]:
        s = np.copy(s)
        s = resize(s, (min_size, min_size, min_size), mode='constant', anti_aliasing=True)
        s = 255*((s - np.min(s))/np.ptp(s))
        s = s.astype('uint8')
        subs.append(s)

    images = []
    for bolacha in range(min_size):
        frame = []
        for s in subs:
            frame.append(np.hstack( (s[bolacha,:,:], s[:,bolacha,:], s[:,:,bolacha]) ))
            
        imgs_comb = np.vstack( (frame[0], frame[1], frame[2], frame[3]) )
        images.append(imgs_comb)
        
    output_file = f'{fname}.gif'
    imageio.mimsave(output_file, images, duration=duration)
 

def myhist(img):
    
    img  = img.ravel()
    hist = []

    for i in range(255):
        occurrences = sum(img[img==i])
        hist.append(occurrences)

    return np.array(hist)


def preprocess(path, fixed_size=127):
    
    sub, sub_raw = load_nii(path)

    ext  = Extractor()

    prob = ext.run(sub) 

    mask = prob < 0.5
    sub[mask] = 0

    sub = cut_on_edges(sub)

    for i in range(sub.shape[0]):
        sub[i,:,:] = cv2.medianBlur(sub[i,:,:],3).astype('uint8')

    for i in range(sub.shape[1]):
        sub[:,i,:] = cv2.medianBlur(sub[:,i,:],3).astype('uint8')

    for i in range(sub.shape[2]):
        sub[:,:,i] = cv2.medianBlur(sub[:,:,i],3).astype('uint8')

    hist = myhist(sub)
    hist = hist[1:]
    hist = medfilt(hist, 7)
    
    peaks, _ = find_peaks(hist, height=500000)

    if len(peaks)<2:
        raise Exception("Não foram encontrados picos suficiente para a segmentação") 
 
    sub_white = np.copy(sub)
    sub_gray  = np.copy(sub)
    sub_csf   = np.copy(sub)

    margin = 10

    threshold = peaks[-1]
    sub_white[sub_white<threshold-margin] = 0
    sub_white[sub_white>0] = 255
    
    threshold = peaks[0]
    sub_gray[sub_gray>threshold+margin] = 0
    sub_gray[sub_gray<threshold-margin] = 0
    sub_gray[sub_gray>0] = 255
    
    sub_csf[sub_csf>threshold-margin] = 0
    sub_csf[sub_csf>0] = 255
    
    common = sub_csf * sub_white * sub_gray

    sub_gray = sub_gray - common    
    sub_gray[sub_gray<0] = 0

    sub_white = sub_white - common    
    sub_white[sub_white<0] = 0
    
    sub_csf = sub_csf - common    
    sub_csf[sub_csf<0] = 0


    return sub_raw, sub, sub_white, sub_gray, sub_csf, margin

# Função principal -------------------------------------------------------------
if __name__ == '__main__':
    
    dataset = pd.read_csv(f'{data_path}/participants.tsv', header=0, sep=r"\s*")

    processed = {c:[] for c in ['sub-ID', 'white-gray-relation', 'white-matter', 'gray-matter', 'csf-matter', 'margin', 'condition', 'file']}

    if os.path.isfile(f'{data_path}/processed.csv'):
        resultsDF = pd.read_csv(f'{data_path}/processed.csv')
        processed   = resultsDF.to_dict('list')
    else:
        resultsDF = None

    for p in dataset['participant_id']:

        file = glob.glob(f'{data_path}anat/{p}*.nii.gz')

        if len(file) >0:

            if resultsDF is not None:
                if len(resultsDF[(resultsDF['sub-ID']==p)])==1:
                    print(f'{p} Já foi processado')
                    continue

            file   = file[0]
            p_data = dataset[dataset['participant_id'].str.match(p)]
            
            fixed_size = 127

            try:
                sub_raw, sub, sub_white, sub_gray, sub_csf, margin = preprocess(file, fixed_size)
            except:
                continue

            create_gif(sub, sub_white, sub_gray, sub_csf, fname=f'{data_path}/gifs/{p}')

            qtd_white = np.sum(sub_white[sub_white>0])
            qtd_gray  = np.sum(sub_gray[sub_gray>0])
            qtd_csf   = np.sum(sub_csf[sub_csf>0])

            processed['sub-ID'].append(p)
            processed['file'].append(file)
            processed['condition'].append(p_data['condit'].tolist()[0])
            processed['white-matter'].append(qtd_white)
            processed['gray-matter'].append(qtd_gray)
            processed['csf-matter'].append(qtd_csf)
            processed['margin'].append(margin)
            processed['white-gray-relation'].append(qtd_white/qtd_gray)

            print(file, p_data['condit'].tolist()[0], qtd_white/qtd_gray)

            df = pd.DataFrame(processed)
            df.to_csv(f'{data_path}/processed.csv', index=False)        
