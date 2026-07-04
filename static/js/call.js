// ======================================================
// PORTAL CALL SERVICE
// call.js
// ======================================================

let calling = false;
let timer = null;
let seconds = 0;

//--------------------------------------------------------
// Inicializar
//--------------------------------------------------------

window.onload = function () {

    document.getElementById("btnCall").disabled = false;
    document.getElementById("btnHangup").disabled = true;

    updateStatus("Listo para llamar", "success");

};

//--------------------------------------------------------
// Estado
//--------------------------------------------------------

function updateStatus(message, color){

    const status=document.getElementById("status");

    status.innerHTML=message;

    status.className="badge bg-"+color;

}

//--------------------------------------------------------
// Cronómetro
//--------------------------------------------------------

function startTimer(){

    seconds=0;

    timer=setInterval(function(){

        seconds++;

        let min=Math.floor(seconds/60);

        let sec=seconds%60;

        if(sec<10)
            sec="0"+sec;

        document.getElementById("timer").innerHTML=
            min+":"+sec;

    },1000);

}

function stopTimer(){

    clearInterval(timer);

    document.getElementById("timer").innerHTML="00:00";

}

//--------------------------------------------------------
// Llamar
//--------------------------------------------------------

function startCall(){

    if(calling)
        return;

    calling=true;

    document.getElementById("btnCall").disabled=true;
    document.getElementById("btnHangup").disabled=false;

    updateStatus("Marcando...", "warning");

    startTimer();

    //----------------------------------------------------
    // AQUÍ irá Portal Call Service
    //----------------------------------------------------

    /*
    fetch("/call/start/"+document.getElementById("contactId").value)
    .then(response=>response.json())
    .then(data=>{

        updateStatus(data.message,"primary");

    });
    */

    setTimeout(function(){

        updateStatus("Llamando...", "primary");

    },2000);

}

//--------------------------------------------------------
// Colgar
//--------------------------------------------------------

function hangupCall(){

    if(!calling)
        return;

    calling=false;

    document.getElementById("btnCall").disabled=false;
    document.getElementById("btnHangup").disabled=true;

    stopTimer();

    updateStatus("Llamada finalizada","danger");

    /*
    fetch("/call/end/"+document.getElementById("contactId").value);
    */

}

//--------------------------------------------------------
// Teclado DTMF
//--------------------------------------------------------

function pressKey(key){

    console.log("DTMF:",key);

}

//--------------------------------------------------------
// Eventos
//--------------------------------------------------------

document.addEventListener("DOMContentLoaded",function(){

    //----------------------------------------------------
    // Botón llamar
    //----------------------------------------------------

    const btnCall=document.getElementById("btnCall");

    if(btnCall){

        btnCall.addEventListener("click",startCall);

    }

    //----------------------------------------------------
    // Botón colgar
    //----------------------------------------------------

    const btnHangup=document.getElementById("btnHangup");

    if(btnHangup){

        btnHangup.addEventListener("click",hangupCall);

    }

    //----------------------------------------------------
    // Teclado
    //----------------------------------------------------

    const keys=document.querySelectorAll(".keypad");

    keys.forEach(function(button){

        button.addEventListener("click",function(){

            pressKey(this.dataset.key);

        });

    });

});