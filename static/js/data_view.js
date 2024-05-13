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

var result2;
function submitdata(data, url_dataview) {
    //Quando chama o model alguns elementos são configurados para serem ocultados 
    $("#resultModal").modal('show');
    document.getElementById("sites").style.display = "none";
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
        var result1 = result.result1;
        result2 = result.result2;

        //Se `result2` for verdadeiro, o corpo do modelo do spinner desaparece e o resultado do gráfico é exibido.
        if (result2 == true) {
            $("#sites_heading").show();
            document.getElementById("modalBody").remove();
            document.getElementById("group").style.display = "inline-flex";
            document.getElementById("sites").style.display = "inline-flex";
            botaoSites(result1);
        } else {
            $('#resultText').html(result1);
            document.getElementById("spinner").style.display = "none";
        }
    });
};
function closePopupResult() {
    //limpa os elementos da lista de botoes quando fecha o model
    var nameSites = document.getElementById("dropdown-list");
    nameSites.innerHTML = '';

    //oculta o conteúdo do gráfico e lista de botoes
    document.getElementById("group").style.display = "none";
    document.getElementById("sites").style.display = "none";

    //se `result2` for falso vai remover o modal-body do spinner para evitar duplicações
    if (result2 == false) {
        document.getElementById("modalBody").remove();
    }

    //criando novamente o modal-body do spinner
    var modalBody = createModalBody();

    var modalContent = document.querySelector('#modalContent');
    modalContent.appendChild(modalBody);

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
}