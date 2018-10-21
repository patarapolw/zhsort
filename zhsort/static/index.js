var isLoading = false;
var spinningLoader = document.getElementById('loader');
var sButton = document.getElementById('submitButton')

sButton.addEventListener('click', function(){
    if(!isLoading){
        isLoading = true;
        spinningLoader.style.visibility = 'visible';
        sButton.disabled = true;

        var http = new XMLHttpRequest();
        var url = '/create';
        var params = {
            text: document.getElementById('textArea1').value
        }

        http.open('POST', url, true);
        http.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
        http.onload = function(){
            if(http.status == 201){
                var filename = JSON.parse(http.responseText).filename;
                window.location = '/excel/' + filename;

                isLoading = false;
                spinningLoader.style.visibility = 'hidden';
                sButton.disabled = false;
            }
        };
        http.send(JSON.stringify(params));
    }
});
