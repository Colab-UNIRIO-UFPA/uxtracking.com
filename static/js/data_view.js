function submitdata(data, url_dataview) {
    $("#resultModal").modal('show');

    $.post(url_dataview, { dir: data }, function (result) {

        if (result) {
            var spinner = document.getElementById("spinner");
            if (spinner) {
                spinner.style.display = "none";
            }
            if (result.plot === "heatmap") {
                var images = JSON.parse(result.images);
                var df_trace = JSON.parse(result.trace);
                var df_voice = JSON.parse(result.voice);

                // Call the graph_heatmap function and handle it asynchronously
                graph_heatmap(images, df_trace, df_voice)
                    .catch((error) => {
                        console.error("Error generating heatmap:", error);
                    });
            } else if (result.plot === "recording") {
                var images = JSON.parse(result.images);
                var icons = JSON.parse(result.icons);
                var df_trace = JSON.parse(result.trace);

                // Call the graph_heatmap function and handle it asynchronously
                graph_recording(images, icons, df_trace)
                    .then(result => {
                        botaoSites(result); // Passar o resultado para a função de criação de botões
                    })
                    .catch(error => {
                        console.error("Error processing recording:", error);
                        $('#resultplot').html('Error processing recording');
                    });
            } else {
                $('#resultplot').html('Invalid or not implemented plot');
            }

        } else {
            $('#resultplot').html('No results returned');
        }
    });
}

function closePopupResult() {
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

// Função para a lista de botões
function botaoSites(result) {
    var nameSites = document.getElementById("dropdown-list");

    // Verificação para expor automaticamente o hover do primeiro site
    var firstItem = true;

    for (const site of Object.keys(result)) {
        var link = document.createElement("a");
        link.setAttribute("class", "list-group-item border border-0");
        link.setAttribute("href", "#");
        link.textContent = site;
        nameSites.appendChild(link);

        // Atribui o evento de clique corretamente
        link.addEventListener("click", handleClick(site));

        if (firstItem) {
            link.click();
            firstItem = false;
        }
    }

    // Define a função de clique
    function handleClick(key) {
        return function (event) {
            event.preventDefault(); // Evitar o comportamento padrão do link
            // Remove a classe "clicked" de todos os botões
            var buttons = document.querySelectorAll('.list-group-item');
            buttons.forEach(function (button) {
                button.classList.remove("clicked");
            });
            // Mostra o conteúdo do ploty
            $('#resultPlot').html(result[key]);
            // Adiciona a classe para alterar a cor de fundo quando o botão é clicado
            this.classList.add("clicked");
        };
    }
}


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
    var dict_site = {}; // Objeto para armazenar os gráficos gerados para cada site

    // Cria uma lista de promessas para processar cada site
    const promises = Object.keys(full_ims).map(site => {
        return new Promise((resolve, reject) => {
            const img = new Image(); // Cria um novo objeto de imagem
            img.src = full_ims[site]; // Define a fonte da imagem

            // Define a função de callback que será executada quando a imagem for carregada
            img.onload = () => {
                const width = img.naturalWidth; // Obtém a largura natural da imagem
                const height = img.naturalHeight; // Obtém a altura natural da imagem

                // Filtra os dados de interação para o site atual
                const filtered_df = df_trace.filter(trace => trace.site === site);
                const traces = []; // Array para armazenar os traces do gráfico

                // Agrupa os dados de interação por tipo
                const groupedData = filtered_df.reduce((acc, trace) => {
                    if (!acc[trace.type]) {
                        acc[trace.type] = [];
                    }
                    acc[trace.type].push(trace);
                    return acc;
                }, {});

                // Cria traces para cada tipo de interação
                for (const type of Object.keys(groupedData)) {
                    const group = groupedData[type];
                    if (type_icon[type]) {
                        const x = group.map(item => item.x);
                        const y = group.map(item => item.y + item.scroll);
                        const time = group.map(item => item.time);
                        const mode = type !== 'click' ? 'lines+markers' : 'markers'; // Define o modo do trace
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
                }

                // Configura o layout do gráfico
                const layout = {
                    xaxis: {
                        range: [0, width],
                        autorange: false,
                        showgrid: false, // Remover linhas de grade
                        zeroline: false, // Remover linha zero
                        visible: false
                    },
                    yaxis: {
                        range: [height, 0],
                        autorange: false,
                        showgrid: false, // Remover linhas de grade
                        zeroline: false, // Remover linha zero
                        visible: false,
                        scaleanchor: 'x'
                    },
                    legend: {
                        orientation: 'h',
                        yanchor: 'bottom',
                        y: 1.02,
                        xanchor: 'left',
                        x: 0,
                        font: { color: 'white', size: 18 }
                    },
                    images: [{
                        source: img.src, // Usa a fonte da imagem carregada
                        xref: 'paper',
                        yref: 'paper',
                        x: 0,
                        y: 1,
                        sizex: 1,
                        sizey: 1,
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

                // Cria um elemento div e plota o gráfico
                const plotDiv = document.createElement('div');
                Plotly.newPlot(plotDiv, traces, layout, { displayModeBar: false });
                dict_site[site] = plotDiv.outerHTML; // Armazena o HTML do gráfico no objeto dict_site
                resolve(); // Resolve a promessa para este site
            };

            img.onerror = reject; // Rejeita a promessa se houver um erro ao carregar a imagem
        });
    });

    // Espera que todas as promessas sejam resolvidas antes de retornar dict_site
    return Promise.all(promises).then(() => {
        return dict_site; // Retorna o objeto dict_site contendo os gráficos gerados
    });
}


function gaussianFilter(matrix, sigma) {
    const kernelSize = Math.ceil(6 * sigma) + 1;
    const kernel = new Array(kernelSize).fill().map((_, i) => {
        const x = i - Math.floor(kernelSize / 2);
        return Math.exp(-0.5 * (x / sigma) ** 2) / (sigma * Math.sqrt(2 * Math.PI));
    });
    const sum = kernel.reduce((acc, val) => acc + val, 0);
    const normalizedKernel = kernel.map(val => val / sum);

    const convolve = (data) => {
        const result = new Array(data.length).fill(0);
        const half = Math.floor(normalizedKernel.length / 2);

        for (let i = 0; i < data.length; i++) {
            let sum = 0;
            for (let j = -half; j <= half; j++) {
                const index = i + j;
                if (index >= 0 && index < data.length) {
                    sum += data[index] * normalizedKernel[j + half];
                }
            }
            result[i] = sum;
        }
        return result;
    };

    const result = matrix.map(row => convolve(row));
    const transposed = result[0].map((_, colIndex) => result.map(row => row[colIndex]));
    return transposed.map(row => convolve(row));
}

async function graph_heatmap(images, df_trace, df_voice) {
    const firstImageKey = Object.keys(images)[0];
    const firstImageBase64 = images[firstImageKey];

    const img = new Image();
    img.src = firstImageBase64;

    await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
    });

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

            const x = plot_df.map(row => {
                const value = parseFloat(row.x);
                return isNaN(value) || value < 0 ? 0 : value;
            });

            const y = plot_df.map(row => {
                const value = Math.abs(parseFloat(row.y) - parseFloat(row.scroll));
                return isNaN(value) || value < 0 ? 0 : value;
            });

            const histogram = new Array(250).fill().map(() => new Array(250).fill(0));
            for (let i = 0; i < x.length; i++) {
                try {
                    const xBin = Math.floor((x[i] / width) * 250);
                    const yBin = Math.floor((y[i] / height) * 250);
                    histogram[xBin][yBin]++;
                } catch (error) {
                    console.error("Erro ao criar o histograma:", error);
                    continue;
                }
            }

            const dataSmoothed = gaussianFilter(histogram, 24);

            if (df_voice.some(row => row.time == time)) {
                const audio2text = df_voice.find(row => row.time == time).text;
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
        xaxis: {
            range: [0, width], autorange: false,
            showgrid: false,
            zeroline: false,
            visible: false,
        },
        yaxis: { 
            range: [0, height], autorange: false, 
            scaleanchor: "x",
            showgrid: false,
            zeroline: false,
            visible: false,
        },
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
    
    // Inicie a plotagem com os dados do primeiro frame
    const initialFrame = frames[0];
    Plotly.newPlot(graphDiv, initialFrame.data, layout, { showlink: false });
    Plotly.addFrames(graphDiv, frames); // Adiciona os frames de animação
}
