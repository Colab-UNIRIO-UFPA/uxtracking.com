var valueData;
function submitdata(data, model) {
    valueData = data;
    document.getElementById("mybutton").style.display = "none";
    $("#resultModal").modal('show');
    $.post("{{ url_for('data_bp.dataanalysis_post', username=username, model=model) }}",
    {
        dir: data
    },
    function(results){
        document.getElementById("spinner").style.display = "none";
        document.getElementById("mybutton").style.display = "inline-block";

        var result1 = results.result1
        var result2 = results.result2

        if (result2 == false){
            document.getElementById("mybutton").style.display = "none";
            $('#resultplot').html(result1);
        }else{
            $('#resultplot').html(renderGraph(result1));
        }
    });
};
function closePopupResult() {
    document.getElementById("spinner").style.display = "inline-flex";
    document.getElementById("mybutton").style.display = "none";
    $('#resultplot').html('')
};
function renderGraph(figJSON){
    var fig = JSON.parse(figJSON)
    var graphDiv = document.getElementById('resultplot');
    Plotly.newPlot(graphDiv, fig.data, fig.layout);
}
function clickbutton(){
    $.post("{{ url_for('data_bp.downloadAudio')}}",
    {
        data: valueData
    },
    function(result){
        let csvAudio = result;
        let blob = new Blob([csvAudio], {type: 'text/csv'});

        const link= window.document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = valueData + '/voice.csv';
        link.click()
        window.URL.revokeObjectURL(link.href);
    });
}