
function updateCountdown() {
    var now = new Date();
    var cdel = document.getElementById("countdown");

    if(end < now) {
        cdel.innerText = "Starting very soon...";
        return;
    }

    var diff = end.getTime() - now.getTime();
    
    var days = Math.floor(diff/86400000).toString();
    var hours = Math.floor((diff % 86400000)/3600000).toString();
    var minutes = Math.floor((diff % 3600000)/60000).toString();
    var seconds = Math.floor((diff % 60000)/1000).toString();

    cdel.innerText = days + " days " + 
                    hours.padStart(2,'0') + ":" + 
                    minutes.padStart(2,'0') + ":" + 
                    seconds.padStart(2,'0') + 
                    " To Go!";
}

setInterval(function() {
    updateCountdown();
}, 1000);
updateCountdown();