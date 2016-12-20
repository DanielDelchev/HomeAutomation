<!doctype html>
<head>
<title>Log in</title>
<body background="static/7.jpg">
<div id="hbox">
  <div class="box">
      <h2>Login</h2>
      <p>Please insert your credentials:</p>
      <form action="login" method="post" name="login">
          <input type="text" name="username" />
          <input type="password" name="password" />
          <br/><br/>
          <button type="submit" > OK </button>
          <button type="button" class="close"> Cancel </button>
      </form>
      <br />
  </div>
</div>
<style>
div {
    text-align: center;
}
</style>
