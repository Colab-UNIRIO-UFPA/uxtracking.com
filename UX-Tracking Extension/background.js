const serverUrl = "http://192.168.100.41:5000";

// Cria um objeto Date com a data e hora atuais
var dataHoraAtual = new Date();

// Extrai as partes da data e hora que queremos incluir no index
var ano = dataHoraAtual.getFullYear();
var mes = ("0" + (dataHoraAtual.getMonth() + 1)).slice(-2);
var dia = ("0" + dataHoraAtual.getDate()).slice(-2);
var hora = ("0" + dataHoraAtual.getHours()).slice(-2);
var minuto = ("0" + dataHoraAtual.getMinutes()).slice(-2);
var segundo = ("0" + dataHoraAtual.getSeconds()).slice(-2);

// Cria a string de index no formato YYYYMMDD-HHMMSS
var dateTime = ano + mes + dia + "-" + hora + minuto + segundo;
var timeInternal = 0;
var userId = '';
chrome.storage.sync.get(["authToken"], function(items){
    debugger;
    // NOTE: check syntax here, about accessing 'authToken'
    userId= items.authToken
});
var domain = "";
var lastTime = 0;
var timeInitial= Math.round(Date.now() / 1000);

chrome.runtime.onMessage.addListener(function (request, sender)
{
    if (request.type == "solicita")
    {
        prepareSample();
    }
    else
    {
        capture(request.type, request.data);
    }
    //sendResponse({ farewell: "goodbye" });
});

let lastCaptureTime = 0;
const captureInterval = 200; // Intervalo em milissegundos entre capturas

function capture(type, data)
{
    const currentTime = Date.now();
    // Verifica se o intervalo mínimo entre capturas foi atingido
    if (currentTime - lastCaptureTime < captureInterval) {
        return;
    }
    chrome.windows.getCurrent(function (win) {   
        chrome.tabs.query({
            active: true,
            lastFocusedWindow: true
        }, function (tabs) {
            if (tabs && tabs[0] && tabs[0].url) {
                var url = new URL(tabs[0].url);
                domain = url.hostname;
                lastCaptureTime = currentTime; // Atualiza o último tempo de captura

                if(type=="eye"){
                    lastTime = data.Time + timeInternal;
                    chrome.tabs.captureVisibleTab(win.id, { format: "jpeg", quality: 25 }, function (screenshotUrl)
                    {
                        data.imageData = screenshotUrl;
                        Post(type, data);
                    });
                }else if(type=="voice"){
                    lastTime = data.Time + timeInternal;
                    chrome.tabs.captureVisibleTab(win.id, { format: "jpeg", quality: 25 }, function (screenshotUrl)
                    {
                        data.imageData = screenshotUrl;
                        Post(type, data);
                    });
                }else{
                    if((type=="move" || type=="freeze")){
                        lastTime = data.Time + timeInternal;
                        chrome.tabs.captureVisibleTab(win.id, { format: "jpeg", quality: 25 }, function (screenshotUrl)
                        {
                            data.imageData = screenshotUrl;
                            Post(type, data);
                        });
                    }
                }
            } else {
                console.error('Nenhuma aba ativa encontrada.');
            }            
        });
    });
}

async function Post(type, data) {
    data.imageName = lastTime + ".jpg";
    const time = new Date().getTime();
  
    try {
      const response = await fetch(`${serverUrl}/receiver`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          metadata: JSON.stringify({
            dateTime: dateTime,
            sample: domain,
            userId: userId,
            type: type,
            time: Math.round(Date.now() / 1000) - timeInitial,
            scroll: data.pageScroll,
            height: data.pageHeight,
            url: data.url
          }),
          data: JSON.stringify(data)
        })
      });
  
      if (response.ok) {
        const responseData = await response.text();
        console.log(type + " " + responseData);
      } else {
        console.error(type + " Request failed with status:", response.status);
      }
    } catch (error) {
      console.error(type + " An error occurred:", error);
    }
  }

function prepareSample() {
    chrome.storage.sync.get(["userid"], function (items) {
        var loadedId = items.userid;
        function useToken(userid) {
            userId = userid;
            chrome.tabs.query({
                active: true,
                lastFocusedWindow: true
            }, async function (tabs) {
                var url = new URL(tabs[0].url);
                domain = url.hostname;
            
                try {
                    const response = await fetch(`${serverUrl}/sample_checker`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ userId: userid, domain: domain, dateTime: dateTime })
                    });
            
                    if (response.ok) {
                        const data = await response.json();
                        timeInternal = parseInt(data);
                    } else {
                        console.error("Request failed with status:", response.status);
                    }
                } catch (error) {
                    console.error("An error occurred:", error);
                }
            });
        }
        if (loadedId !== null && loadedId !== "" && typeof loadedId  !== 'undefined') {
            useToken(loadedId);
        }
        else {
            chrome.storage.sync.set({ 'userid': userId }, function () {
                // Notify that we saved.
                useToken(loadedId);
            });
        }
    });
}


var id = 0;

