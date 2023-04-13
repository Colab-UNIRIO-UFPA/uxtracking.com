const serverUrl = "http://127.0.0.1:5000";

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
var userId = "fb50a10f11b0c153e88e96d06668911f";
var domain = "";
var lastTime = 0;
var fixtime=0;

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
var shot=5;
function capture(type, data)
{
    chrome.windows.getCurrent(function (win) {   
        chrome.tabs.getSelected(null, function (tab) {
            var url = new URL(tab.url);
            domain = url.hostname;
            //if(lastTime == (Math.ceil(data.Time) + timeInternal)&& ((type=="move" || type=="freeze") && //Math.ceil(data.Time) % 3 == 1)){
            //    data.imageData = "";
            //}
            if(type=="eye"){
                data.imageData = "NO";
                //data.Time-=0.2;
                Post(type, data);
            }else{
				if((type=="move" || type=="freeze") && shot<7){
					data.imageData = "NO";
					Post(type, data);              
					shot++;
				}
				else{
					shot=0;
					lastTime = data.Time + timeInternal;
					chrome.tabs.captureVisibleTab(win.id, { format: "jpeg", quality: 25 }, function (screenshotUrl)
					{
						data.imageData = screenshotUrl;
						Post(type, data);
					});

				}
			}
        });
    });
}

function Post(type, data){
	data.imageName = lastTime+".jpg";
	if(fixtime<data.Time + timeInternal){
		fixtime=data.Time + timeInternal;
	}
    $.post(serverUrl+"/receiver",
                {
                    metadata: JSON.stringify({
                            dateTime: dateTime,
                            sample: domain,
                            userId: userId,
                            type: type,
                            time: fixtime,
                            scroll: data.pageScroll,
                            height: data.pageHeight,
                            url: data.url
                    }),
                    data: JSON.stringify(data)

            }
			).fail(function (data){
				console.log(type+" "+data);
			}	
			
			).done(function (data) {
                console.log(type+" "+data);
                }
            );
}

function prepareSample() {
    chrome.storage.sync.get(["userid"], function (items) {
        var loadedId = items.userid;
        function useToken(userid) {
            userId = userid;
            chrome.tabs.getSelected(null, function (tab) {
                var url = new URL(tab.url);
                domain = url.hostname;
                $.post(serverUrl+"/sample_checker", { userId: userid, domain: domain, dateTime: dateTime}).done(function (data) {
                    timeInternal = parseInt(data);});
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
function init() {
    //alert("Mouse pos "+posX+" "+posY);
}

chrome.browserAction.onClicked.addListener(function (tab) {
    chrome.storage.sync.remove(["userid"], function(Items) {
        loadedId == null;
    });
    alert('Data Cleaned.');
});

chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
    //alert("reloaded");
    //chrome.tabs.executeScript(tabId, { file: "content.js" });
});

