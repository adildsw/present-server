$(document).ready(function() {

  //Connect Database Button
  $("#btnConnectDB").click(function() {
    if($("#btnConnectDB").hasClass("green"))
      window.location = "/";
    else {
      var http = new XMLHttpRequest();
      var url = '/connect_db';

      var ip = $('input[name="db-host-ip"]').val();
      var port = $('input[name="db-host-port"]').val();
      var user = $('input[name="db-username"]').val();
      var pwd = $('input[name="db-password"]').val();
      var authdb = $('input[name="db-auth"]').val();

      var flag = true;
      $(".input").removeClass("error");
      if(ip == "")
        $('input[name="db-host-ip"]').parent().addClass("error");
      if(port == "")
        $('input[name="db-host-port"]').parent().addClass("error");
      if(user == "")
        $('input[name="db-username"]').parent().addClass("error");
      if(pwd == "")
        $('input[name="db-password"]').parent().addClass("error");
      if(authdb == "")
        $('input[name="db-auth"]').parent().addClass("error");
      if($(".input").hasClass("error"))
        flag = false;

      if(flag) {
        var params = "".concat("ip=", ip,
                              "&port=", port,
                              "&user=", user,
                              "&pwd=", pwd,
                              "&authdb=", authdb);

        http.open('POST', url, true);
        http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        http.onreadystatechange = function() {
          if(this.readyState == 4 && this.status == 200) {
            $(".field").removeClass("disabled");
            $("#btnConnectDB").removeClass("loading disabled");

            var res = JSON.parse(this.responseText);

            if(res["connected"] == false) {
              $("#btnConnectDB").addClass("orange");
              $("#btnConnectDB span").text("Connect");
              alert(res["message"]);
            }
            else if(res["connected"] == true) {
              $(".field").addClass("disabled");
              $("#btnConnectDB").addClass("green");
              $("#btnConnectDB span").text("Continue");
            }
          }
        }

        $(".field").addClass("disabled");
        $("#btnConnectDB").addClass("loading disabled");
        $("#btnConnectDB").removeClass("orange");
        http.send(params);
      }
    }
  });

  //Get Started Button
  $("#btnGetStarted").click(function() {
    var http = new XMLHttpRequest();
    var url = '/org_reg';

    var name = $('input[name="org-name"]').val();
    var pwd = $('input[name="reg-pwd"]').val();
    var cnf_pwd = $('input[name="reg-cnf-pwd"]').val();

    var flag = true;
    $(".input").removeClass("error");
    if(name == "")
      $('input[name="org-name"]').parent().addClass("error");
    if(pwd == "")
      $('input[name="reg-pwd"]').parent().addClass("error");
    if(cnf_pwd == "")
      $('input[name="reg-cnf-pwd"]').parent().addClass("error");
    if($(".input").hasClass("error"))
      flag = false;

    if(pwd != cnf_pwd) {
      alert("ERROR: Passwords don't match.")
      flag = false;
    }

    if(flag) {
      var params = "".concat("org_name=", name, "&admin_pwd=", pwd);

      http.open('POST', url, true);
      http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
      http.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200) {
          var res = JSON.parse(this.responseText);

          if(res["status"] == "S0") {
            window.location = "/";
          }
          else {
            alert(res["message"]);
          }
        }
      }
      http.send(params);
    }
  });

  // Faculty Login
  $("#faculty_login_bt").click(function() {
    var url = "\login_auth";
    var username = $('input[name="faculty_login_username"]').val();
    var pwd = $('input[name="faculty_login_pwd"]').val();
    var params = "".concat("user=", username, "&pwd=", pwd);
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] == "S0") {
        window.location = "/dashboard";
      }
      else {
        alert(res['message']);
      }
    }
    console.log('hi');
    $.fn.postRequest(url, params, callback); // Attempting to Log In
  });

  //Login Administrator
  $("#btnLoginAdmin").click(function() {
    var http = new XMLHttpRequest();
    var url = '\login_auth'

    var admin_pwd = $('input[name="admin-pwd"]').val();

    var flag = true;
    $(".input").removeClass("error");
    if(admin_pwd == "")
      $('input[name="admin-pwd"]').parent().addClass("error");
    if($(".input").hasClass("error"))
      flag = false;

    if(flag) {
      var params = "".concat("user=admin&pwd=", admin_pwd);

      http.open('POST', url, true);
      http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
      http.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200) {
          var res = JSON.parse(this.responseText);

          if(res["status"] == "S0") {
            window.location = "/dashboard";
          }
          else {
            alert(res["message"]);
          }
        }
      }
      http.send(params);
    }

  });

  //Retry Database Connection Button
  $("#btnRetry").click(function() {
    window.location = '/';
  });

  //Reconfigure Database Connection Button
  $("#btnReconfig").click(function() {
    var http = new XMLHttpRequest();
    var url = "/load";
    var params = "reconfig=true";

    http.open('POST', url, true);
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    http.onreadystatechange = function() {
      if(this.readyState == 4 && this.status == 200) {
        var loadedPage = document.open("text/html", "replace");
        loadedPage.write(this.responseText);
        loadedPage.close();
      }
    }
    http.send(params);
  });

  //For Tab-element Functionality
  $('.menu .item').tab();
});
