var ws = null;
$(function(){
    $("#bt").on('click',function(){
        ws = new WebSocket('ws://localhost:9999/logs');
        $("#bt").attr('disabled', true);
        ws.onopen = function() {
            console.log("open......")
            ws.onmessage = function( event ) {
                console.log( event );
            }
            ws.onclose = function() {
                console.log( "close...." );
                $("#bt").attr('disabled', false);
            }
        }
        ws.onerror = function() {
            console.log("web socket Error....");
            $("#bt").attr('disabled', false);
        }
    });
    $("#bt").attr('disabled', true);
    setTimeout(function(){
        $("#bt").attr('disabled', false);
    },1000);
});