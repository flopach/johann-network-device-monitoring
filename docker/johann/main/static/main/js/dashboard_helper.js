/* 
Javascript for johann
*/

// menu bar - open/close function
$(document).ready(function(){

    function change_drawer(element_id) { 
        if ( $(element_id).hasClass("sidebar__drawer--opened") ) {
            $(element_id).removeClass("sidebar__drawer--opened");
            $(element_id).addClass("sidebar__drawer--closed");
        }
        else {
            $(element_id).removeClass("sidebar__drawer--closed");
            $(element_id).addClass("sidebar__drawer--opened");
        }
    }   

    $("#drawer_devices").on("click", function() { 
        change_drawer.call(this, "#drawer_devices")
    });

    $("#drawer_tools").on("click", function() { 
        change_drawer.call(this, "#drawer_tools")
    });

    $("#drawer_reports").on("click", function() { 
        change_drawer.call(this, "#drawer_reports")
    });

});

// Websocket Stuff when getting information from the celery tasks
function task_status(task_type) {
    const response_output = JSON.parse(document.getElementById('response_output').textContent);
        
    const StatusSocket = new WebSocket(
        'ws://'+window.location.host+'/ws/status/'
    );

    function request_task_status(e) {
        StatusSocket.send(JSON.stringify(
        {
            "type" : task_type,
            "task_id": response_output
        }));
    }

    /* When task was created, message/task_id is sent. If received, start getting the task info via WS */
    if (response_output) {
        StatusSocket.onopen = function(e) {
            request_task_status();
    }};
        
    /* Display the incoming message */
    StatusSocket.onmessage = function(e) {
        const msg = JSON.parse(e.data);
        //console.log(msg);

        if (msg.type == "t_status") {
            $('#status_box').html('<div class="alert alert--info"> \
            <div class="loader loader--small" aria-label="Loading, please wait..."><div class="wrapper"><div class="wheel" id="status_wheel"></div></div></div> \
            <div style="flex-grow: 1; margin-left:5%; align-self:center;">'+msg.content+'</div></div>');
            setTimeout(request_task_status, 2000); // keep requesting the task status until finished every 2 seconds
        }
        else if (msg.type == "t_result") {

            if (msg.content[0] == 200) {
                $('#status_box').html('<div class="alert alert--success"><div class="alert__icon icon-check-outline"></div> \
                <div class="alert__message">'+msg.content[1]+'</div></div>');
            }
            else {
                $('#status_box').html('<div class="alert alert--danger" role="alert"><div class="alert__icon icon-error-outline"></div> \
                <div class="alert__message">'+msg.content[1]+'</div></div>');
            }

        }
        else if (msg.type == "t_content_result") {

            if (msg.content[0] == 200) {
                $('#status_box').html('<div class="alert alert--success"><div class="alert__icon icon-check-outline"></div> \
                <div class="alert__message">Task finished!</div></div>');

                $('#result').html(msg.content[1]);
            }
            else {
                $('#status_box').html('<div class="alert alert--danger" role="alert"><div class="alert__icon icon-error-outline"></div> \
                <div class="alert__message">'+msg.content[1]+'</div></div>');
            }

        }
        else {
            console.log("Error: Wrong status msg!");
        }

    };

    StatusSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };
}


// scrolling for the logs page
function scroll_bottom() {
    $("html, body").animate({
        scrollTop: $("#scroll").height()
    }, 1000);
}

