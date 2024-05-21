function submitdata(data, url_dataview) {
    $("#resultModal").modal('show');

    $.post(url_dataview, { dir: data }, function (result) {

        if (result) {
            document.getElementById("spinner").style.display = "none";

            var images = JSON.parse(result.images);
            var df_trace = JSON.parse(result.trace);
            var df_voice = JSON.parse(result.voice);

            // Call the graph_heatmap function and handle it asynchronously
            graph_heatmap(images, df_trace, df_voice)
                .catch((error) => {
                    console.error("Error generating heatmap:", error);
                });
        } else {
            $('#resultplot').html('No results returned');
        }
    });
}

function closePopupResult() {
    //coletaAberta == false; //coleta fechada

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

function gaussianFilter(matrix, sigma) {
    const kernelSize = 6 * sigma + 1;
    const kernel = new Array(kernelSize).fill().map((_, i) => {
        const x = i - kernelSize / 2;
        return Math.exp(-0.5 * (x / sigma) ** 2) / (sigma * Math.sqrt(2 * Math.PI));
    });
    const sum = kernel.reduce((acc, val) => acc + val, 0);
    return matrix.map(row => row.map(val => val / sum));
}

async function graph_heatmap(images, df_trace, df_voice) {
    // Obter a primeira imagem do JSON
    const firstImageKey = Object.keys(images)[0];  // Obtém a primeira chave (ID) do JSON
    const firstImageBase64 = images[firstImageKey];  // Obtém a primeira imagem em base64

    // Criar uma nova imagem e carregar a imagem base64 nela
    const img = new Image();
    img.src = firstImageBase64;

    // Retornar uma Promise para garantir que a imagem foi carregada
    await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
    });

    // Obter a largura e altura da imagem
    const width = img.width;
    const height = img.height;

    const frames = [];
    const colorscale = [
        [0, "rgba(255, 255, 255, 0)"],
        [0.15, "rgba(180, 180, 255, 0.45)"],
        [0.25, "rgba(160, 255, 160, 0.55)"],
        [0.45, "rgba(255, 255, 90, 0.65)"],
        [0.65, "rgba(255, 200, 100, 0.75)"],
        [0.85, "rgba(255, 90, 50, 0.85)"],
        [1, "rgba(255, 1, 0, 1)"]
    ];


    const maxTime = Math.max(...df_trace.map(row => row.time));
    for (let time = 0; time <= maxTime; time++) {
        const filtered_df = df_trace.filter(row => row.time == time);
        const uniqueImages = [...new Set(filtered_df.map(row => row.image))];
        
        for (const image of uniqueImages) {
            const plot_df = filtered_df.filter(row => row.image == image);

            const x = plot_df.map(row => parseFloat(row.x));
            const y = plot_df.map(row => Math.abs(parseFloat(row.y) - parseFloat(row.scroll)));

            // Create histogram
            const histogram = new Array(250).fill().map(() => new Array(250).fill(0));
            try {
                for (let i = 0; i < x.length; i++) {
                    const xBin = Math.floor((x[i] / width) * 250);
                    const yBin = Math.floor((y[i] / height) * 250);
                    histogram[xBin][yBin]++;
                }
            } catch (error) {
                console.error("Erro ao criar o histograma:", error);
                continue;
                // Lidar com o erro, se necessário
            }

            const dataSmoothed = gaussianFilter(histogram, 12);

            if (df_voice.some(row => row.time == time)) {
                const audio2text = df_voice.find(row => row.time == time).text;
                console.log(`Audio Frame pushed`);
                frames.push({
                    data: [{
                        z: dataSmoothed,
                        type: 'heatmap',
                        colorscale: colorscale,
                        showscale: false,
                        hovertemplate: "Posição X: %{x}<br>Posição Y: %{y}"
                    }],
                    name: `${time}`,
                    layout: {
                        images: [{
                            source: images[image],
                            xref: "x",
                            yref: "y",
                            x: 0,
                            y: height,
                            sizex: width,
                            sizey: height,
                            sizing: "stretch",
                            opacity: 1,
                            layer: "below"
                        }],
                        annotations: [{
                            x: 0.5,
                            y: 0.04,
                            xref: "paper",
                            yref: "paper",
                            text: `Falado: ${audio2text}`,
                            font: {
                                family: "Courier New, monospace",
                                size: 18,
                                color: "#ffffff"
                            },
                            bordercolor: "#c7c7c7",
                            borderwidth: 2,
                            borderpad: 8,
                            bgcolor: "rgb(36, 36, 36)",
                            opacity: 1
                        }]
                    }
                });
            } else {
                console.log(`Frame pushed`);
                frames.push({
                    data: [{
                        z: dataSmoothed,
                        type: 'heatmap',
                        colorscale: colorscale,
                        showscale: false,
                        hovertemplate: "Posição X: %{x}<br>Posição Y: %{y}"
                    }],
                    name: `${time}`,
                    layout: {
                        images: [{
                            source: images[image],
                            xref: "x",
                            yref: "y",
                            x: 0,
                            y: height,
                            sizex: width,
                            sizey: height,
                            sizing: "stretch",
                            opacity: 1,
                            layer: "below"
                        }]
                    }
                });
            }
        }
    }

    const layout = {
        xaxis: { range: [0, width], autorange: false },
        yaxis: { range: [0, height], autorange: false, scaleanchor: "x" },
        images: [{
            source: firstImageBase64,
            xref: "x",
            yref: "y",
            x: 0,
            y: height,
            sizex: width,
            sizey: height,
            sizing: "stretch",
            opacity: 1,
            layer: "below"
        }],
        sliders: [{
            steps: frames.map(f => ({
                args: [[f.name], { frame: { duration: 0, redraw: true }, mode: "immediate" }],
                label: f.name,
                method: "animate"
            })),
            x: 0,
            y: -0.07,
            font: { size: 12 },
            ticklen: 4,
            currentvalue: { prefix: "Time(s):", visible: true }
        }],
        updatemenus: [{
            buttons: [{
                args: [null, { frame: { duration: 800, redraw: true }, fromcurrent: true, transition: { duration: 300, easing: "quadratic-in-out" } }],
                label: "Play",
                method: "animate"
            }, {
                args: [[null], { frame: { duration: 0, redraw: true }, mode: "immediate", transition: { duration: 0 } }],
                label: "Pause",
                method: "animate"
            }],
            direction: "left",
            pad: { r: 0, t: 0, b: 0, l: 0 },
            showactive: false,
            type: "buttons",
            x: 0.12,
            xanchor: "right",
            y: -0.02,
            yanchor: "top",
            bgcolor: "rgb(190, 190, 190)",
            font: { color: "rgb(0, 0, 0)" }
        }]
    }

    var graphDiv = document.getElementById('resultPlot');

    Plotly.newPlot(graphDiv, [], layout, { showlink: false }); // Inicia a plotagem sem dados
    Plotly.addFrames(graphDiv, frames); // Adiciona os frames de animação
}
