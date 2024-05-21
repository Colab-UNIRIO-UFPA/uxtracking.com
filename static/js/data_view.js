function submitdata(data, url_dataview) {
    $("#resultModal").modal('show');
    $.post(url_dataview,
    {
        dir: data
    },
    function (result) {
        document.getElementById("spinner").style.display = "none";
        $('#resultPlot').html(result);
    });
};
function closePopupResult() {
    document.getElementById("spinner").style.display = "inline-flex";
    $('#resultPlot').html('');
};

var result4;
var coletaAberta; //verificando se a coleta está aberta
function submitdata(data, url_dataview) {

    coletaAberta = true;

    //Quando chama o model alguns elementos são configurados para serem ocultados 
    document.getElementById("sites").style.display = "none";
    $("#resultModal").modal('show');
    $("#sites_heading").hide();
    document.getElementById("group").style.display = "none";

    //criando o modal-body para o spinner
    var modalBody = createModalBody();

    var modalContent = document.querySelector('#modalContent');
    modalContent.appendChild(modalBody);

    //solicitação para a rota dataview
    $.post(url_dataview,
    {
        dir: data
    },
    function (result) {
        //Quando recebe o resultado os dados são exibidos seja gráfico ou texto
        var type_icon = JSON.parse(result.result2); //type_icon
        var df_trace_site = JSON.parse(result.result3); //df_trace
        result4 = JSON.parse(result.result4);
        //botaoSites(result); 
        //Se `result4` for verdadeiro, o corpo do modelo do spinner desaparece e o resultado do gráfico é exibido.
        if (coletaAberta == true && result4 == true) {
            modalSpinner = true;
            var full_ims = JSON.parse(result.result1); //full_ims
            //var img = JSON.parse(result.result4)
            //var w = JSON.parse(result.result5)
           // var h = JSON.parse(result.result6)
   
            $("#sites_heading").show();
            document.getElementById("modalBody").remove();
            document.getElementById("group").style.display = "inline-flex";
            document.getElementById("sites").style.display = "inline-flex";
            //console.log("retorno: ", graph_recording(full_ims, type_icon, df_trace_site));
            var graph = graph_recording(full_ims, type_icon, df_trace_site);
            console.log("graph: ", graph);
            botaoSites(graph); 
            
        } else {
            var result1 = result.result1; 
            $('#resultText').html(result1);
            document.getElementById("spinner").style.display = "none";
        }
    });
};
function closePopupResult() {
    coletaAberta == false; //coleta fechada

    //limpa os elementos da lista de botoes quando fecha o model
    var nameSites = document.getElementById("dropdown-list");

    nameSites.innerHTML = '';

    //verificando se o modelBody existe
    var modalBody = document.getElementById("modalBody"); 

    //oculta o conteúdo do gráfico e lista de botoes
    document.getElementById("group").style.display = "none";
    document.getElementById("sites").style.display = "none";

    //se existir remove
    if (modalBody !== null) {
        modalBody.remove();
    }

    //criando novamente o modal-body do spinner
    var modalBody = createModalBody();
    var modalContent = document.querySelector('#modalContent');
    modalContent.appendChild(modalBody);

    //limpando o plotly
    $('#resultPlot').html('');

    // Aqui, definimos um atraso de 1000 milissegundos (1 segundo) antes de remover o modal-body do spinner
    setTimeout(function () {
        document.getElementById("modalBody").remove();
    }, 1000);
};
/*
function botaoSites(result) {
    var nameSites = document.getElementById("dropdown-list");

    // Verificação para expor automaticamente o hover do primeiro site
    var firstItem = true;

    // Imprime o objeto result para verificar seu conteúdo
    console.log("Resultado recebido:", result);

    // Checa se nameSites existe no DOM
    if (!nameSites) {
        console.error("Elemento 'dropdown-list' não encontrado no DOM.");
        return;  // Encerra a função se não encontrar o elemento
    }

    // Itera sobre cada chave em result
    Object.keys(result).forEach(function(key) {
        console.log("Processando a chave:", key);  // Log para verificação

        var link = document.createElement("a");
        link.setAttribute("class", "list-group-item border border-0");
        link.setAttribute("href", "#");
        link.textContent = key;
        nameSites.appendChild(link);

        // Atribui o evento de clique usando a função handleClick
        link.addEventListener("click", handleClick(key));

        if (firstItem) {
            link.click();
            firstItem = false;  // Garante que o clique automático ocorra apenas no primeiro item
        }
    });
}

function handleClick(key) {
    return function() {
        console.log("oi")
        // Remove a classes "clicked" de todos os botões
        var buttons = document.querySelectorAll('.list-group-item');
        buttons.forEach(function(button) {
            button.classList.remove("clicked");
        });

        // Mostra o conteúdo do Plotly
        $('#resultPlot').html(result[key]);

        // Adiciona a classe "clicked" ao botão clicado
        this.classList.add("clicked");
    };
}*/


//funcao para a lista de botoes
function botaoSites(result) {
    var nameSites = document.getElementById("dropdown-list");

    //verificação para expor automaticamente o hover do primeiro site
    var firstItem = true;
    
    console.log("rr: ", result);

    Object.keys(result).forEach(function(key) { 
        console.log("teste01...");
    });
    
    for (var key in result) {
        console.log("teste02...");
    };
    //console.log("test 01", result)
    for (var key in result) {
        if (result.hasOwnProperty(key)) {
            var link = document.createElement("a");
            link.setAttribute("class", "list-group-item border border-0");
            link.setAttribute("href", "#");
            console.log("key", key)
            link.textContent = key;
            nameSites.appendChild(link);

            // Atribui o evento de clique usando a função handleClick
            link.addEventListener("click", handleClick(key));

            if (firstItem) {
                link.click();
                firstItem = false;
            }
        }
    };
    //console.log("tst", result);
    // Define a função de clique
    function handleClick(key) {
        return function () {
            // Remove a classe "clicked" de todos os botões
            var buttons = document.querySelectorAll('.list-group-item');
            buttons.forEach(function (button) {
                button.classList.remove("clicked");
            });
            console.log(key)
            //mostra o conteúdo do ploty
            $('#resultPlot').html(result[key]);
            // Adiciona a classe para alterar a cor de fundo quando o botao e clicado
            this.classList.add("clicked");
        };
    }
};

    /*
    Object.keys(result).forEach(function(key) {    
        console.log("Processando a chave:", key);  // Log para verificação

        var link = document.createElement("a");
        link.setAttribute("class", "list-group-item border border-0");
        link.setAttribute("href", "#");
        link.textContent = key;
        nameSites.appendChild(link);

        // Atribui o evento de clique usando a função handleClick
        link.addEventListener("click", handleClick(key));

        if (firstItem) {
            link.click();
            firstItem = false;  // Garante que o clique automático ocorra apenas no primeiro item
        }
    });*/

// cria o elemento modal-body do spinner
function createModalBody() {
    var modalBody = document.createElement('div');
    modalBody.className = 'modal-body h-100 d-flex align-items-center justify-content-center gap-3';
    modalBody.id = 'modalBody';

    // Criação do elemento list-group
    var listGroup = document.createElement('div');
    listGroup.className = 'list-group';

    // Criação do elemento list-group-item
    var listGroupItem = document.createElement('div');
    listGroupItem.className = 'list-group-item';

    // Criação do elemento spinner
    var spinner = document.createElement('div');
    spinner.className = 'spinner-border text-secondary';
    spinner.id = 'spinner';
    spinner.setAttribute('role', 'status');

    var resultText = document.createElement('div');
    resultText.id = 'resultText';

    // Adicionando o spinner e o resultText ao list-group-item
    listGroupItem.appendChild(spinner);
    listGroupItem.appendChild(resultText);

    // Adicionando o list-group-item ao list-group
    listGroup.appendChild(listGroupItem);

    // Adicionando o list-group ao modal-body
    modalBody.appendChild(listGroup);

    // Retorna o modal-body para ser usado posteriormente
    return modalBody;
};

function graph_recording(full_ims, type_icon, df_trace) {

    //const dict_site = {};
    var dict_site = new Object();

    console.log(full_ims);
    console.log(type_icon);
    console.log(df_trace);
    

    // Processa cada site
    Object.keys(full_ims).forEach(site => {
        // Criar nova imagem
        const img = new Image();
        //alert("oi")
        // Função para processar os dados após a imagem estar carregada
        img.onload = () => {
            //alert("oi");
            // Agora podemos acessar as dimensões da imagem
            const width = img.naturalWidth;
            const height = img.naturalHeight;
            //alert(width);
            //alert(height);

            // Filtra os dados de interação para o site atual
            const filtered_df = df_trace.filter(trace => trace.site === site);
            const traces = [];

            // Agrupar dados por tipo de interação
            const groupedData = filtered_df.reduce((acc, trace) => {
                if (!acc[trace.type]) {
                    acc[trace.type] = [];
                }
                acc[trace.type].push(trace);
                return acc;
            }, {});

            // Criar traces para cada tipo de interação
            Object.keys(groupedData).forEach(type => {
                const group = groupedData[type];
                if (type_icon[type]) {
                    const x = group.map(item => item.x);
                    //console.log("x: ", x)
                    const y = group.map(item => item.y + item.scroll);
                    //console.log("y: ", y)
                    const time = group.map(item => item.time);
                    const mode = type !== 'click' ? 'lines+markers' : 'markers';
                    const text = time.map(t => {
                        const hours = String(Math.floor(t / 3600)).padStart(2, '0');
                        const minutes = String(Math.floor((t % 3600) / 60)).padStart(2, '0');
                        const seconds = String(t % 60).padStart(2, '0');
                        return `Time: ${hours}:${minutes}:${seconds}`;
                    });

                    traces.push({
                        x: x,
                        y: y,
                        mode: mode,
                        name: type,
                        text: text,
                        hovertemplate: `Interaction: ${type}<br>Site: ${site}<br>%{text}<br>X: %{x}<br>Y: %{y}</br>`,
                        marker: {
                            symbol: type_icon[type],
                            size: type !== 'click' ? 10 : 35,
                            angleref: 'previous'
                        }
                    });
                }
            });

            // Configurar o layout do gráfico
            const layout = {
                xaxis: { range: [0, width], 
                        autorange: false, 
                        rangeslider: { visible: false } },
                yaxis: { range: [height, 0], 
                        autorange: false, 
                        scaleanchor: 'x' },
                legend: { orientation: 'h', 
                        yanchor: 'bottom', 
                        y: 1.02, 
                        xanchor: 'left', 
                        x: 0, 
                        font: { color: 'white', size: 18 } },
                images: [{
                    source: img.src, // Usar a fonte já carregada
                    xref: 'x',
                    yref: 'y',
                    x: 0,
                    y: height,
                    sizex: width,
                    sizey: height,
                    sizing: 'stretch',
                    opacity: 1,
                    layer: 'below'
                }],
                width: width * 0.6,
                height: height * 0.6,
                margin: { l: 0, r: 0, t: 0, b: 0 },
                paper_bgcolor: 'rgba(0, 0, 0, 0)',
                plot_bgcolor: 'rgba(0, 0, 0, 0)'
            };

            // Criar um elemento div e plotar o gráfico
            const plotDiv = document.createElement('div');
            Plotly.newPlot(plotDiv, traces, layout, { displayModeBar: false });
            //dict_site[site] = plotDiv.outerHTML;
            dict_site[site] = plotDiv.outerHTML;
        };
        img.src = full_ims[site];
        //console.log(img.src);
    });
    console.log("Resultado da função: ", dict_site);
    return dict_site;
}


/*
function graph_recording(full_ims, type_icon, df_trace){
    console.log(full_ims)
    console.log(type_icon)
    console.log(df_trace)
    
    const dict_site = {};

    Object.keys(full_ims).forEach(site => {
        const filtered_df = df_trace.filter(trace => trace.site === site);

        const img = new Image();

        
        // Definir a fonte da imagem para a string base64
        img.src = full_ims[site];
        img_src = img.src
        
        // Acessar largura e altura
        const width = img.width;
        const height = img.height;
        console.log(width)
        console.log(height)
        
        const traces = [];

        const groupedData = filtered_df.reduce((acc, trace) => {
            if (!acc[trace.type]) {
                acc[trace.type] = [];
            }
            acc[trace.type].push(trace);
            return acc;
        }, {});

        Object.keys(groupedData).forEach(type => {
            const group = groupedData[type];
            if (type_icon[type]) {
                const x = group.map(item => item.x);
                //console.log(x)
                const y = group.map(item => item.y + item.scroll);
                //console.log(y)
                const time = group.map(item => item.time);
                //console.log(time)

                const mode = type !== 'click' ? 'lines+markers' : 'markers';
                const text = time.map(t => {
                    const hours = String(Math.floor(t / 3600)).padStart(2, '0');
                    const minutes = String(Math.floor((t % 3600) / 60)).padStart(2, '0');
                    const seconds = String(t % 60).padStart(2, '0');
                    return `Time: ${hours}:${minutes}:${seconds}`;
                });

                traces.push({
                    x: x,
                    y: y,
                    mode: mode,
                    name: type,
                    text: text,
                    hovertemplate: `Interaction: ${type}<br>Site: ${site}<br>%{text}<br>X: %{x}<br>Y: %{y}</br>`,
                    marker: {
                        symbol: type_icon[type],
                        size: type !== 'click' ? 10 : 35,
                        angleref: 'previous'
                    }
                });
            }
        });

        const layout = {
            xaxis: {
                range: [0, width],
                autorange: false,
                rangeslider: { visible: false }
            },
            yaxis: {
                range: [height, 0],
                autorange: false,
                scaleanchor: 'x'
            },
            legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: 1.01,
                xanchor: 'left',
                x: 0,
                font: { color: 'white', size: 18 }
            },
            images: [{
                source: img.src,
                xref: 'x',
                yref: 'y',
                x: 0,
                y: height,
                sizex: width,
                sizey: height,
                sizing: 'stretch',
                opacity: 1,
                layer: 'below'
            }],
            width: width * 0.6,
            height: height * 0.6,
            margin: { l: 0, r: 0, t: 0, b: 0 },
            paper_bgcolor: 'rgba(0, 0, 0, 0)',
            plot_bgcolor: 'rgba(0, 0, 0, 0)'
        };

        const plotDiv = document.createElement('div');
        Plotly.newPlot(plotDiv, traces, layout, { displayModeBar: false });

        dict_site[site] = plotDiv.outerHTML;
    });
    console.log("dict: ", dict_site)
    return dict_site;
}
*/
/*
    //criado para guardar o site e seu plotly
    var dict_site = {
        //nome do site: {plotly}
        //exemplo de como tem que ficar
        "www.youtube.com": 'plotly1',
        'www.plotly,com': 'plotly2',
    };

        //ao final e dentro do loop for adicione o nome do site e seu plotly no dict
    return dict_site;
}   
*/



