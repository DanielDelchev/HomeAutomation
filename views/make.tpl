<!doctype html>
<html>
    <head>
        <body background="static/1.jpg">
        <title>Make_appointments</title>
        <script type="text/javascript" src="/static/jquery.js"></script>
        <link rel="stylesheet" href="/static/bootstrap.min.css">
        <script src="/static/bootstrap.min.js"></script>


        <script type="text/javascript">

       	$( document ).ready(function() { //on lauch 
			timers();
		});
        
        
        
        function back_to_buttons(){
            window.location.href="/home_page"
        }
        
        function show_R1(){
            window.location.href="/show_R1"
        }
        
        function show_R2(){
            window.location.href="/show_R2"
        }
        
        /////////
        function auto_change_state_relay(relay){
            if (relay == 'relay1'){
                document.getElementById('submit1').disabled = true;
                var Y_on = document.getElementById('Year1').value;
                var M_on = document.getElementById('Month1').value;
                var D_on = document.getElementById('Day1').value;
                var H_on = document.getElementById('Hour1').value;
                var Min_on = document.getElementById('Minute1').value;
                var S_on = document.getElementById('Second1').value;
                var Y_off = document.getElementById('Year11').value;
                var M_off = document.getElementById('Month11').value;
                var D_off = document.getElementById('Day11').value;
                var H_off = document.getElementById('Hour11').value;
                var Min_off = document.getElementById('Minute11').value;
                var S_off = document.getElementById('Second11').value;
            }
            
            if (relay == 'relay2'){
                document.getElementById('submit2').disabled = true;
                var Y_on = document.getElementById('Year2').value;
                var M_on = document.getElementById('Month2').value;
                var D_on = document.getElementById('Day2').value;
                var H_on = document.getElementById('Hour2').value;
                var Min_on = document.getElementById('Minute2').value;
                var S_on = document.getElementById('Second2').value;
                var Y_off = document.getElementById('Year22').value;
                var M_off = document.getElementById('Month22').value;
                var D_off = document.getElementById('Day22').value;
                var H_off = document.getElementById('Hour22').value;
                var Min_off = document.getElementById('Minute22').value;
                var S_off = document.getElementById('Second22').value; 
            }         
            
            
            if ( 
                (Y_on == null || Y_on =="")||
                (M_on == null || M_on =="")||
                (D_on == null || D_on =="")||
                (H_on == null || H_on =="")||
                (Min_on == null || Min_on =="")||
                (S_on == null || S_on =="")||
                
                (Y_off == null || Y_off =="")||
                (M_off == null || M_off =="")||
                (D_off == null || D_off =="")||
                (H_off == null || H_off =="")||
                (Min_off == null || Min_off =="")||
                (S_off == null || S_off =="")
                ){
                    alert("You have left a field unfilled!")
                    return false;
                };
            
            
            var date_on = new Date(Y_on,M_on-1,D_on,H_on,Min_on,S_on,0);
            var date_off = new Date(Y_off,M_off-1,D_off,H_off,Min_off,S_off,0);

            var epoch_time_now = get_server_epoch_time()
            var now = new Date(epoch_time_now*1000);
            var epoch_time_on = Math.round(date_on.getTime()/1000);
            var epoch_time_off = Math.round(date_off.getTime()/1000);   
            
            var epoch_time_until_on = epoch_time_on - epoch_time_now;
            var epoch_time_until_off = epoch_time_off - epoch_time_now;
            
            var string_on = date_on.toString(); //strings 
            var string_off = date_off.toString(); //strings
            
            if ((date_off < now) || (date_on < now) || (string_on == string_off)){ 
                alert('Invalid input!One event is in the past or events match in time!')
                if (relay == 'relay1'){
                    document.getElementById('submit1').disabled = false;
                }
                if (relay == 'relay2'){
                    document.getElementById('submit2').disabled = false;
                }
                return None
            }
            
            var MAX_TIMEOUT = 4017600 //roughly mounth and a half in seconds
            var MIN_TIMEOUT = 18 // 15 + 3 (3 sec for the calculation of the dates in html ?)
            if (epoch_time_until_on > MAX_TIMEOUT || epoch_time_until_off > MAX_TIMEOUT){ 
                alert('Invalid input!Event too far ahead in the future!(Do not surpass 45 days)')
                if (relay == 'relay1'){
                    document.getElementById('submit1').disabled = false;
                }
                if (relay == 'relay2'){
                    document.getElementById('submit2').disabled = false;
                }
                return None
            }     
            if (epoch_time_until_on < MIN_TIMEOUT || epoch_time_until_off < MIN_TIMEOUT){ 
                alert('Invalid input!Event too close ahead in the future!(Cannot be less than 15 sec)')
                if (relay == 'relay1'){
                    document.getElementById('submit1').disabled = false;
                }
                if (relay == 'relay2'){
                    document.getElementById('submit2').disabled = false;
                }
                return None
            }

            
            var reversed = false
            if (date_off < date_on){
                reversed = true
            }
            jQuery.ajax({
				url: "/auto_relay",
				type: "POST",
				data: JSON.stringify({str_on : string_on ,str_off : string_off ,rev : reversed, epoch_on : epoch_time_on ,epoch_off : epoch_time_off, rel_number : relay}),
				contentType: 'application/json',
                async: false, 
                cache: false,
				success: function(data) {
                if (relay == 'relay1'){
                    document.getElementById('submit1').disabled = false;
                }
                if (relay == 'relay2'){
                    document.getElementById('submit2').disabled = false;
                } 
                }
				});
        } 
                             
        
        
        function get_server_epoch_time(){
            var result_time;
            jQuery.ajax({
				url: "/epoch_time",
                type: "GET",
                async: false,
				success: function(data) {
                    result_time = data.epoch 
                }
            });
            return result_time;
        }
        
        function erase_all_R1(){
            jQuery.ajax({
				url: "/eraseR1",
                type: "GET",
                async: false,
                cache: false,
				success: function(data) {
                    location.reload(true)   
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
        <br>
		<h3> Back to buttons: </h3>
		<button type="back" id="back" onclick="back_to_buttons()" class="btn btn-primary btn-bg">Back</button>
		<br>

                
       <form>
          <fieldset action="">
          <legend>Relay 1 appointment:</legend>
            
            <h3 id="S1">On:</h3>  
            Year:
            <input type="number" name="Year1" id="Year1" min="2015" max="2100" value="2016" >
            Month:
            <input type="number" name="Month1" id="Month1" min="1" max="12" value="12" >
            Day:
            <input type="number" name="Day1" id="Day1" min="1" max="31" value="6" >
            Hour:
            <input type="number" name="Hour1" id="Hour1" min="0" max="23" value="20" >
            Minute:
            <input type="number" name="Minute1" id="Minute1" min="0" max="59" value="30" >            
            Second:
            <input type="number" name="Second1" id="Second1" min="0" max="59" value="0" >  

            <h3 id="E1">Off:</h3>              
            Year:
            <input type="number" name="Year11" id="Year11" min="2015" max="2100" value="2016" >
            Month:
            <input type="number" name="Month11" id="Month11" min="1" max="12" value="12" >
            Day:
            <input type="number" name="Day11" id="Day11" min="1" max="31" value="6" >
            Hour:
            <input type="number" name="Hour11" id="Hour11" min="0" max="23" value="20" >
            Minute:
            <input type="number" name="Minute11" id="Minute11" min="0" max="59" value="31" >            
            Second:
            <input type="number" name="Second11" id="Second11" min="0" max="59" value="0" >  

            <input id="submit1" type="submit" onclick="auto_change_state_relay('relay1')">
            
            </fieldset>
        </form>
                
        <br>
		<h3> Show appointments for Relay1: </h3>
		<button type="button" id="S1" onclick="show_R1()" class="btn btn-primary btn-sm">Show</button>
		<br>

        <br>
		<h3> Erase ALL appointments for Relay1: </h3>
        <button type="button" id="C1" onclick="erase_all_R1()" class="btn btn-danger">erase</button>
		<br>
        
        <h1> Server time(ABIDE BY IT!): </h1>
        <p id="Timer_server"></p>
        
        <h3> Your time: </h3>
        <p id="Timer_local"></p>
        
        
        <form action="">
          <fieldset>
          <legend>Relay 2 appointment:</legend>
            
            <h3 id="S2">On:</h3>
            Year:
            <input type="number" name="Year2" id="Year2" min="2015" max="2050" value="2016" >
            Month:
            <input type="number" name="Month2" id="Month2" min="1" max="12" value="12" >
            Day:
            <input type="number" name="Day2" id="Day2" min="1" max="31" value="6" >
            Hour:
            <input type="number" name="Hour2" id="Hour2" min="0" max="23" value="20" >
            Minute:
            <input type="number" name="Minute2" id="Minute2" min="0" max="59" value="30" >            
            Second:
            <input type="number" name="Second2" id="Second2" min="0" max="59" value="0" >  

            <h3 id="E2">Off:</h3>            
            Year:
            <input type="number" name="Year22" id="Year22" min="2015" max="2050" value="2016" >
            Month:
            <input type="number" name="Month22" id="Month22" min="1" max="12" value="12" >
            Day:
            <input type="number" name="Day22" id="Day22" min="1" max="31" value="6" >
            Hour:
            <input type="number" name="Hour22" id="Hour22" min="0" max="23" value="20" >
            Minute:
            <input type="number" name="Minute22" id="Minute22" min="0" max="59" value="31" >            
            Second:
            <input type="number" name="Second22" id="Second22" min="0" max="59" value="0" >  
            
            <input id="submit2" type="submit" onclick="auto_change_state_relay('relay2')">
            
            </fieldset>
        </form>
        
        <br>
		<h3> Show appointments for Relay2: </h3>
		<button type="button" id="S2" onclick="show_R2()" class="btn btn-primary btn-sm">Show</button>
		<br>

        <br>
		<h3> Erase ALL appointments for Relay2: </h3>
        <button type="button" id="C2" onclick="erase_all_R2()" class="btn btn-danger">erase</button>
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