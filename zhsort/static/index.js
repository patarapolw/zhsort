var isLoading = false;
var loader = document.getElementById('loader');
var sButton = document.getElementById('submitButton')

sButton.addEventListener('click', function(){
    if(!isLoading){
        isLoading = true;
        loader.style.visibility = 'visible';
        sButton.disabled = true;
        loader.innerHTML = '<li>Loading...</li>';

        var xhr = new XMLHttpRequest();
        var url = '/create';
        var params = {
            text: document.getElementById('textArea1').value
        }
        var position = 0;
        function handleData(){
            var messages = xhr.responseText.split('\n');
            var latest = '';

            messages.forEach(function(value) {
                try {
                    var jsonLatest = JSON.parse(value);
                    if(jsonLatest.simplified) latest = 'Loading vocab: ' + jsonLatest.simplified;
                    else if(jsonLatest.hanzi) latest = 'Loading Hanzi: ' + jsonLatest.hanzi;
                    else latest = value;
                } catch (err) {
                    latest = value;
                }

                var item = document.createElement('li');
                item.textContent = latest;
                loader.appendChild(item);
                loader.scrollTop = loader.scrollHeight;
            });
            position = messages.length - 1;

            return latest;
        }

        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify(params));
        var timer = setInterval(function() {
            // check the response for new data
            var latest = handleData();
            if (xhr.readyState == XMLHttpRequest.DONE) {
                clearInterval(timer);
                window.location = '/excel/' + latest;

                isLoading = false;
                loader.style.visibility = 'hidden';
                sButton.disabled = false;
            }

            // stop checking once the response has ended
            if (xhr.readyState == XMLHttpRequest.DONE) {
                clearInterval(timer);
                latest.textContent = 'Done';
            }
        }, 1000);
    }
});
