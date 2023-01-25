function link(x) {
    var url = x.href;
    var guia = window.open(url, '_blank');
    guia.focus();
    console.log(url) 
    }