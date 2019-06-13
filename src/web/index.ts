import "bootstrap/scss/bootstrap.scss";
import "bootstrap";
import { createExcel, IExport } from "./xlsx";

let isLoading = false;
const loader = document.getElementById('loader') as HTMLDivElement;
const sButton = document.getElementById('submitButton') as HTMLButtonElement;
const textArea1 = document.getElementById("textArea1") as HTMLTextAreaElement;

sButton.addEventListener('click', function(){
    if(!isLoading){
        isLoading = true;
        loader.style.visibility = 'visible';
        sButton.disabled = true;
        loader.innerHTML = '<li>Loading...</li>';

        const xhr = new XMLHttpRequest();
        const url = '/api/generate';
        const params = {
            entry: textArea1.value
        }
        function handleData() {
            const messages = xhr.responseText.split('\n');
            messages.forEach((value) => {
                if (value[0] === "{") {
                    const d = JSON.parse(value);
                    let msg = "";
                    if (d.simplified) {
                        msg = `Receiving vocab ${d.simplified}`
                    } else {
                        msg = `Receiving hanzi ${d.entry}`
                    }

                    var item = document.createElement('li');
                    item.textContent = msg;
                    loader.appendChild(item);
                    loader.scrollTop = loader.scrollHeight;
                }
            });

            return xhr.responseText;
        }

        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify(params));
        var timer = setInterval(function() {
            // check the response for new data
            handleData();
            if (xhr.readyState == XMLHttpRequest.DONE) {
                clearInterval(timer);

                isLoading = false;
                loader.style.visibility = 'hidden';

                const x: IExport = {
                    vocab: [],
                    hanzi: []
                };

                let currentRowType = "vocab";
                for (const row of xhr.responseText.split("\n")) {
                    if (row[0] !== "{") {
                        currentRowType = row;
                    } else {
                        try {
                            (x as any)[currentRowType].push(JSON.parse(row));
                        } catch (e) {}
                    }
                }

                createExcel(x, (s) => {
                    var item = document.createElement('li');
                    item.textContent = s;
                    loader.appendChild(item);
                    loader.scrollTop = loader.scrollHeight;
                }).then(() => {
                    sButton.disabled = false;
                });
            }

            // stop checking once the response has ended
            if (xhr.readyState == XMLHttpRequest.DONE) {
                clearInterval(timer);
            }
        }, 1000);
    }
});
