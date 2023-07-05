![Badge](https://img.shields.io/badge/VS%20Code-1.60-information?style=flat&logo=Visual-Studio-Code&logoColor=white&color=007ACC)
 # UX-Tracking: User eXperience Tracking
Repositório destinado a abrigar o código-fonte de todas as aplicações relacionadas ao ecossistema da ferramenta UX-Tracking.




## Tabela de conteúdos

*  [Pre Requisitos](#pre-requisitos)
*  [Registo do usuário](#Registro)
*  [Módulos](#Módulos)
* * [Cliente](#cliente)
* * * [Rastreamento de mouse](#rastreamento-de-mouse)
* * * [Rastreamento ocular](#rastreamento-ocular)
* * * [Keylogging](#keylogging)
* * * [Think aloud](#Transcrição-de-voz)
* * [Armazenamento](#armazenamento)
* * [Web App](#Web-App)
* * [Visualizador](#Visualizador)
* * * [Reprodução de sessão](#reproducao-de-sessao)
* * * [Rastreamento ocular](#rastreamento-ocular)
* * * [Análise de métricas](#analise-de-metricas)
* * * [Download do estudo](#download-do-estudo)
*  [Tecnologias](#tecnologias)

 ## Pré-requisitos

📃 Para a abertura dos projetos contidos neste repositório, estabelecem-se os seguintes requisitos:

*  [Python](https://www.python.org/)
*  [Visual Studio Code](https://code.visualstudio.com/download)
*  [Google Chrome](https://www.google.com/chrome/)

## Registro
Para o registro do usuário, será necessário e-mail e senha. Sendo possível recuperar a senha caso perdida. Cada usuário tem suas próprias pesquisas armazenadas em sua conta.
## Módulos
A UX-Tracking é constituída de 3 módulos: Cliente, Web App e visualizador. Os três módulos são responsáveis respectivamente por coletar dados de interação; organizar e armazenar; e prover formas de visualizar os dados capturados. Os módulos são descritos a seguir.
### Cliente
Desenvolvido como uma extensão do navegador Google Chrome utilizando Javascript, este módulo é responsável por capturar - do lado cliente - as interações dos desenvolvedores, no papel de usuários do portal, a partir das técnicas de rastreamento do mouse, do olho e do teclado, além de transcrição de fala. As versões do módulo cliente encontram-se no diretório `clients`.


#### Rastreamento de mouse
A captura de interações do mouse contempla 4 tipos de interação:
* Movimento
* Clique
* Pausa
#### Rastreamento ocular
O rastreamento ocular é realizado por meio de uma versão modificada do [WebGazer](https://github.com/brownhci/WebGazer) (Copyright © 2016-2021, Brown HCI Group).
#### Keylogging
A extensão também pode capturar entradas de teclado, registrando a digitação de caracteres.
#### Transcrição de voz
Utilizando o [WebKit Voice Recognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition), o módulo cliente é capaz de capturar voz, incluindo pausas, transcrevendo e enviando como entradas de texto.

### Web App
Após o registro do usuário, a aplicação web, através do login do usuário, disponibilizará os dados coletados, de forma condensada, para o usuário através de um CSV com data e hora da coleta. Os dados do CSV incluem sites visitados, voz, rastreio do mouse e rastreio dos olhos. 

### Pós-processamento de dados
A aplicação conta, atualmente, com quatro módulos de pós-processamento de dados de dados, sendo eles:
#### K-means clustering
Este componente, ou submódulo, reproduz individualmente cada amostra capturada, conforme a escolha do usuário permitindo a visualização dos dados clusterizados do modelo de agrupamento k-means.
#### Agglomerated-Cluster
Este componente produz um agrupamento hierárquico de clusters, conforme a entrada do usuário, e é um método de análise de cluster que busca construir uma hierarquia de clusters.
#### Mean-Shift-Clustering
Este componente gera o deslocamento médio do dado de entrada escolhido pelo usuário.

### Visualizador
A aplicação desktop é responsável por permitir a visualização dos dados. Possui três recursos de visualização, descritos a seguir:
#### Reprodução de sessão
Este componente, ou submódulo, reproduz individualmente cada amostra capturada, permitindo a visualização quadro-a-quadro dos movimentos do desenvolvedor registrados a partir das técnicas de rastreamento domouse e do olho. Para a composição da visualização, o módulo utiliza captura de telas registradas durante a interação, e sobre essas posiciona pontos e linhas contínuas representando o caminho percorrido e ações realizadas pelo usuário.
#### Mapa de calor
Este componente produz um mapa de calor para o rastreamento do mouse e do olho. É possível a geração de mapas individuais ou de grupo de desenvolvedores. As representações são constituídas de capturas de tela sobrepostas e encontradas nos dados capturados, de forma a reproduzir a tela da aplicação. Este componente permite a detecção de áreas de interesse, desvios de atenção, zonas não visualizadas, entre outras possibilidades.
#### Análise de métricas

#### Download do estudo
O procedimento:<br/>
1º - Acesse o link -> https://uxtracking.andrepereira.eng.br/ <br/>
2º - Clique no botão "Download Research" <br/>
Após os passos acima, o download do zip da pasta Samples será iniciado. <br/>
Para o download da ferramenta de visualização, basta clicar no botão "Ferramenta de Pós-processamento" e o download será iniciado. <br>
## Tecnologias
* [JavaScript](https://www.javascript.com/)
* [Python](https://www.python.org/)
* [HTML](https://developer.mozilla.org/pt-BR/docs/Web/HTML)
* [CSS](https://developer.mozilla.org/pt-BR/docs/Web/CSS)
