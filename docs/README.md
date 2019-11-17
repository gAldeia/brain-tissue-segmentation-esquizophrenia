# Estratégia para Segmentação de Tecidos Cerebrais, e o uso de Aprendizado de Máquina para validação dos resultados

![](sub-11.gif)

Dentre as variações estruturais no cérebro, podemos citar um aumento do volume dos ventrículos laterais, e um desvio na relação entre massa branca (conexões entre neurônios) e massa cinzenta (corpos celulares de neurônios).

Uma das tarefas comumente envolvida nas aplicações de visão computacional é a segmentação de objetos. Em uma imagem de ressonância, podemos utilizar métodos de segmentação para separar as massas branca e cinzenta, e então calcular a relação entre elas, buscando associar essa relação ao diagnóstico.

Estudos comprovaram que há uma dilatação dos ventrículos laterais, e uma alteração da proporção entre massa cinzenta e massa branca \cite{structuralbrainchanges} em pacientes com esquizofrenia. Uma forma de quantificar isso para usar em classificadores é associar uma imagem com a razão massa branca/massa cinzenta, e usar esses dados associados com o diagnóstico.

Dito isso, devido às alterações estruturais conhecidas que ocorrem em cérebros de pacientes esquizofrênicos e, por apresentam potencial de serem medidas por métodos de visão computacional, a proposta do projeto é criar uma \textit{pipeline} de pré-processamento de imagens de ressonância (focando apenas no aspecto anatômico/estrutural), com o objetivo de utilizar os dados processados em modelos de aprendizado de máquina, e medir a acurácia obtida.

-----

# Instalação e uso

Para executar o projeto em sua máquina, você deve:
1. Clonar este repositório e instalar todas as bibliotecas necessárias;
2. Executar cada um dos scripts na ordem em que estão numerados.

Após executar esses scripts, o repositório estará configurado para rodar os notebooks em ./docs/!

As versões das bibliotecas utilizadas foram:
|Biblioteca | Versão |
| --- | --- |
| nilear | 0.5.0 |
| nibabel  | 2.3.3 |
| scipy  | 1.1.0 |
| deepbrain  | 0.1 |
| numpy  | 1.15.1 |
| matplotlib  | 2.3.3 |
| pandas  | 0.23.4 |
| opencv-python  | 3.4.3 |