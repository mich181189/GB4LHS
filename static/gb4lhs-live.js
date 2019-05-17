

function getStatus() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', "/api/getstatus", true);
    xhr.responseType = 'json';
    xhr.onload = function() {
        var status = xhr.status;
        if (status === 200) {
            el = document.getElementById("livestatusbox");
            indicator = document.getElementById("onairindicator");
            if(xhr.response['onair']) {
                el.innerHTML = "";
                for(var key in xhr.response['status']) {
                    el.innerHTML += "<span class=\"liveinfoheader\">"+key+"</span><span class=\"liveinfodata\">"+xhr.response['status'][key]+"</span><br>";
                }
                indicator.innerHTML = "<span class=\"status badge badge-pill badge-success\">ON AIR</span>";
            }
            else
            {
                el.innerHTML = "<span class=\"liveinfoheader\">Currently Not Operating</span>";
                indicator.innerHTML = "<span class=\"status badge badge-pill btn-secondary\">OFF AIR</span>";
            }
            document.getElementById("qsosbox").innerHTML = xhr.response['contacts'];

            setTimeout(function() {
                getStatus();
            }, xhr.response['refresh-in']);
        } else {
            console.log("Failed to get status")
        }
    };
    xhr.send();
}

function process_qso(qso) {
    contacts = document.getElementById("contactslist");

    var newrow = document.createElement("tr");
    newrow.innerHTML =      "<td>"+qso['date']+"</td>" +
                            "<td>"+qso['time']+"</td>" +
                            "<td>"+qso['callsign']+"</td>" +
                            "<td>"+qso['frequency']+"</td>" +
                            "<td>"+qso['mode']+"</td>" +
                            "<td>"+qso['report_recv']+"</td>" +
                            "<td>"+qso['report_sent']+"</td>";

    while(contacts.childElementCount >= 10) {
        contacts.removeChild(contacts.lastChild);
    }
    if(contacts.childElementCount > 0) {
        contacts.insertBefore(newrow, contacts.childNodes[0]);
    } else {
        contacts.appendChild(newrow);
    }
}

function getQSOs() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', "/api/getqsos/since/"+last_qso_timestamp, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
        var status = xhr.status;
        if (status === 200) {
            
            if(xhr.response['last'] > 0) {
                last_qso_timestamp = xhr.response['last'];

            }

            for(var qso in xhr.response['qsos']) {
                process_qso(xhr.response['qsos'][qso]);
            }

            setTimeout(function() {
                getQSOs();
            }, xhr.response['refresh-in']);
        } else {
            console.log("Failed to get status")
        }
    }
    xhr.send();
}

setTimeout(function() {
    getQSOs();
}, 10000);

getStatus();