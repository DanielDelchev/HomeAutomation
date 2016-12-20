<!doctype html>
<head>
  <body background="static/7.jpg">
<div id='main'>
    <title>Admin page</title>
    <h2>Administration page</h2>
    <p>Welcome {{current_user.username}}, your role is: {{current_user.role}}</p>
    <div id='commands'>
      <p>Create new user:</p>
      <form action="create_user" method="post">
          <p><label>Role</label> <input type="text" name="role" /></p>
          <p><label>Username</label> <input type="text" name="username" /></p>
          <p><label>Password</label> <input type="password" name="password" /></p>
          <button type="submit" > OK </button>
          <button type="button" class="close"> Cancel </button>
      </form>
      <br />
      <p>Delete user:</p>
      <form action="delete_user" method="post">
          <p><label>Username</label> <input type="text" name="username" /></p>
          <button type="submit" > OK </button>
          <button type="button" class="close"> Cancel </button>
      </form>
    <div id="users">
        <table>
            <tr><th>Username</th><th>Role</th><th>
            %for u in users:
            <tr><td>{{u[0]}}</td><td>{{u[1]}}</td><td>
            %end
        </table>
        <p>(Reload page to refresh)</p>
        <br/>
        <table>
            <tr><th>Role</th><th>Level</th></tr>
            %for r in roles:
            <tr><td>{{r[0]}}</td><td>{{r[1]}}</td></tr>
            %end
        </table>
    </div>

    <div class="clear"></div>

    
    
    <br>
    <h3> Log out. </h3>
    <button type="button" id="lout" onclick="logout()" class="btn btn-primary btn-sm">logout</button>
    <br>   
    
    <br>
    <h3> Homepage. </h3>
    <button type="button" id="hpage" onclick="home()" class="btn btn-primary btn-sm">home</button>
    <br> 
    
    <div id="urls">    
    </div>
        <script src="/static/jquery.js"></script>
        <script src="/static/bootstrap.min.js"></script>
    <script>
    //when a some form is submitted post to 'action' the serialized input in json format
        $('form').submit(function() {
            $.post($(this).attr('action'), $(this).serialize(), "json");
            return false;
        });
        
       function logout(){
            window.location.href="/logout"
        }

       function home(){
            window.location.href="/home_page"
        }
        
    </script>
</div>

