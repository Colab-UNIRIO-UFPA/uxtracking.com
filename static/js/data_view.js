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


        //Se `result4` for verdadeiro, o corpo do modelo do spinner desaparece e o resultado do gráfico é exibido.
        if (coletaAberta == true && result4 == true) {
            modalSpinner = true;
            var full_ims = JSON.parse(result.result1); //full_ims

            $("#sites_heading").show();
            document.getElementById("modalBody").remove();
            document.getElementById("group").style.display = "inline-flex";
            document.getElementById("sites").style.display = "inline-flex";
            botaoSites(graph_recording(full_ims, type_icon, df_trace_site)); 
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

//funcao para a lista de botoes
function botaoSites(result) {
    var nameSites = document.getElementById("dropdown-list");

    //verificação para expor automaticamente o hover do primeiro site
    var firstItem = true;

    // Define a função de clique
    function handleClick(key) {
        return function () {
            // Remove a classe "clicked" de todos os botões
            var buttons = document.querySelectorAll('.list-group-item');
            buttons.forEach(function (button) {
                button.classList.remove("clicked");
            });

            //mostra o conteúdo do ploty
            $('#resultPlot').html(result[key]);

            // Adiciona a classe para alterar a cor de fundo quando o botao e clicado
            this.classList.add("clicked");
        };
    }

    //cria os elementos dentro da div com id ´dropdown-list´
    for (var key in result) {
        if (result.hasOwnProperty(key)) {
            var link = document.createElement("a");
            link.setAttribute("class", "list-group-item border border-0");
            link.setAttribute("href", "#");

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
};
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
function graph_recording(full_ims, type_icon, df_trace_site){

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


