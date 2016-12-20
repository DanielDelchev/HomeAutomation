<!doctype html>
<html>
    <head>
        <body background="static/1.jpg"> 
        
        <title>Home</title>
        <script type="text/javascript" src="/static/jquery.js"></script>
        <link rel="stylesheet" href="/static/bootstrap.min.css">

        <script src="/static/bootstrap.min.js"></script>
        
        <script type="text/javascript">


        

		$( document ).ready(function() { //on lauch 
			init();
		});
        
		function initState(relay, data){
			image = document.getElementById(relay+"_image");
			operation = document.getElementById(relay+"_value")
		    
            if(data == "on"){ //if relay has been turned on, the button should now have off effect
				image.src="/static/off.png"
                operation.value = "off"  //next operation to perform on hit of button
                jQuery('#' + relay + '_text').html("Device is working.");
			}
            
			else{ //if relay has been turned off, the button should now have on effect
                image.src="/static/on.png"
				operation.value = "on" //next operation to perform on hit of button
				jQuery('#' + relay + '_text').html("Device is NOT  working.");
			}

		}

		function change_state(relay){
            document.getElementById(relay).disabled = true;
            operation = document.getElementById(relay+"_value")  // get button' s effect (to which state it should be changed)
			
            jQuery.ajax({
				url: "/"+relay,
				type: "POST",
				data: JSON.stringify({op : operation.value }),
				contentType: 'application/json',
                async: false,
				success: function(data) {
				jQuery('#' + relay + '_text').html(data).hide().fadeIn(500);
				document.getElementById(relay).disabled = false;
				image = document.getElementById(relay+"_image"); 

				initState(relay, data);
				}
				});
		}

        
        function init(){
            setInterval("getState()",1000)
        }
        
		function getState(){
			jQuery.ajax({
				url: "/state",
				type: "GET",
				success: function(data) { // get state of relays on server and initiate viewer's variables
					initState("relay1", data.relay1);
					initState("relay2", data.relay2);
                    server_time();
                    local_time();
                    }
				});
		}

        function shut_down(){
                jQuery.ajax({
				url: "/shut_down",
				type: "GET",
				});
        }


		function stop(){
			jQuery.ajax({
				url: "/stop",
				type: "GET",
				success: function(data) { //refresh images before shutting down
					initState("relay1", "off");
					initState("relay2", "off");
                },
            	complete: function(data) { //shut down server
                    jQuery('#' + 'stopper_text').html("Shut down:True");
                    shut_down();
                }
				});
		}
        
       function appoint(){
            window.location.href="/appoint"
        }

       function logout(){
            window.location.href="/logout"
        }

       function admin(){
            window.location.href="/admin"
        }
        

       function server_time(){
            jQuery.ajax({
			url: "/server_time",
			type: "GET",
			success: function(data) {
                    document.getElementById('Timer_server').innerHTML = data.time
                },
           error:function(data) {
                    document.getElementById('Timer_server').innerHTML = "Server is offline"
                }
			});
		}
        
       function local_time(){
            var now = new Date();
            document.getElementById('Timer_local').innerHTML = now;
		}
        
       
	   </script>
       
    </head>
    <h2>Welcome {{current_user.username}}, your role is: {{current_user.role}}</h2>
    <body>
	<div class="container">
	<div class="jumbotron" align="center">
		
        <br>
		<h3 id="relay1_text">Device is NOT working.</h3>
		<button id="relay1" onclick = "change_state('relay1')">
			<img id="relay1_image" src="/static/on.png"  height="42" width="42">
		</button>
		<br>
        
        <br>
        <h3 id="relay2_text">Device is NOT working.</h3>
		<button id="relay2" onclick = "change_state('relay2')">
            <img id="relay2_image" src="/static/on.png"  height="42" width="42">
		</button>
		<br>
        
		<input type="hidden" id="relay1_value" value="on">  <!--the values which the relays would take AFTER the next pressing of a button-->
		<input type="hidden" id="relay2_value" value="on">  <!--the opposite state of the actual current state of the relays-->
		
        <br>
        <h3 id="stopper_text">Shut down:False</h3>
		<button class="btn btn-danger" onclick = "stop()">STOP</button>
        <br>
</div>
</div> 

		<h1> Server time(ABIDE BY IT!): </h1>
        <p id="Timer_server"></p>
        
        <h3> Your time: </h3>
        <p id="Timer_local"></p>
     
        <br>
		<h3> Make appointment. </h3>
		<button type="button" id="apnt" onclick="appoint()" class="btn btn-primary btn-sm">Make</button>
		<br>

        <br>
		<h3> Log out. </h3>
		<button type="button" id="lout" onclick="logout()" class="btn btn-primary btn-sm">logout</button>
		<br>   
        
        <br>
		<h3> Admin page(classified). </h3>
		<button type="button" id="admn" onclick="admin()" class="btn btn-primary btn-sm">admin</button>
		<br>           

        
    </body>
</html>


