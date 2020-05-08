/*
|---------------------------------------------------------------------------
| Helper Functions
|---------------------------------------------------------------------------
|
| This section contains helper functions used throughout the program for
| tasks like making POST requests or changing the UI Content to load the
| selected window from the navigation sidebar and the likes.
|
*/


/*
* Function for Making POST Request
*
* $.fn.postRequest(url, params, callback): takes three arguments "url",
* "params" and "callback" to make a POST request.
*
* Arguments
* url: (String) URL where the POST request is to be made.
*
* params: (String) parameters to be passed along with the POST request.
*
* callback: (Function) function to be executed once the POST request returns
* a 200 status. The callback function takes the POST request's responseText
* as an argument.
*
*/
$.fn.postRequest = function(url, params, callback) {
  var http = new XMLHttpRequest();
  http.open("POST", url, true);
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  http.onreadystatechange = function() {
    if(this.readyState == 4 && this.status == 200) {
      callback(this.responseText);
    }
  }
  http.send(params);
}

// Function to Log Out User
$.fn.logOut = function() {
  var url = "/logout";
  var params = "";
  var callback = function(responseText) {
    window.location = "/login";
  }
  $.fn.postRequest(url, params, callback); // Making POST request to logout
}
