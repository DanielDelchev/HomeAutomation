<!doctype html>
<html>
    <head>
        <body background="static/5.jpg">
        <title>Relay2_appointments</title>
        <script type="text/javascript" src="/static/jquery.js"></script>
        <link rel="stylesheet" href="/static/bootstrap.min.css">
        <script src="/static/bootstrap.min.js"></script>
        
        <br>
        <h1>Relay2 Appointments (in server time!):</h1>
        </br>
        
        <p id="content"></p>
        
        <script type="text/javascript">
        
        $( document ).ready(function() { //on lauch 
			show_list();
            timers();
		});
        
        
        function back_to_buttons(){
            window.location.href="/home_page"
        }
        
        function back_to_appointments(){
            window.location.href="/appoint"
        }
        
        function show_list(){
            jQuery.ajax({
				url: "/get_R2_appointments",
                type: "GET",
                async: false,
                cache: false,
				success: function(data) {
                    document.getElementById('content').innerHTML = data.content
                }
				});   
        }
        
        function erase_all_R2(){
            jQuery.ajax({
				url: "/eraseR2",
                type: "GET",
                async: false,
                cache: false,
				success: function(data) {
                    location.reload(true)   
                }
            });
        }
        

        function remove_singleR2(){
            document.getElementById('submitID').disabled = true;
            var ID_number = document.getElementById('ID').value;
            
            jQuery.ajax({
				url: "/remove_singleR2",
				type: "POST",
				data: JSON.stringify({ID : ID_number}),
				contentType: 'application/json',
                async: false, 
                cache: false,
				success: function(data) {
				document.getElementById('submitID').disabled = false; 
                }
				});
        
        }

        
        function timers(){
            setInterval("server_time()",1000);
            setInterval("local_time()",1000);
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
        
       function logout(){
            window.location.href="/logout"
        }

       function admin(){
            window.location.href="/admin"
        }
        
        
        </script>
    </head>
    <body>
    
    
        <form>
            <fieldset action="">
            <legend>Remove a single appointment with ID:</legend>
            <input type="text" name="ID" id="ID" value="" >
            <input id="submitID" type="submit" onclick="remove_singleR2()">
            </fieldset>
        </form>    

        
        <h1> Server time(ABIDE BY IT!): </h1>
        <p id="Timer_server"></p>
        
        <h3> Your time: </h3>
        <p id="Timer_local"></p>
        
        
        
        <br>
		<h3> Back to buttons: </h3>
		<button type="back" id="back" onclick="back_to_buttons()" class="btn btn-primary btn-bg">Back</button>
		<br>

        <br>
		<h3> Back to appointment making: </h3>
		<button type="back2" id="back2" onclick="back_to_appointments()" class="btn btn-primary btn-bg">Back</button>
		<br>
            
        <br>
        <h3 id="eraser">Erase ALL appointments for Relay2:</h3>
		<button type="erase" id="erase" onclick="erase_all_R2()" class="btn btn-danger">erase</button>
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