$(document).ready(function() {
  /*
  |---------------------------------------------------------------------------
  | UI Toggles
  |---------------------------------------------------------------------------
  |
  | This section contains all UI toggle actions like sidebars and popups.
  |
  */

  // Reloader Variable
  var reloader_variable = "";


  // Sidebar Toggle
  $("#sidebar_toggle_bt").click(function() {
    $('.ui.sidebar').sidebar('toggle');
  });


  // Popup, Sidebar and QR Code Toggle
  $(document).on("change", "#content", function() {
    $("button").popup();
    $('.ui.dropdown').dropdown();

    // Checking if Session Attendance Page
    if($("#qr_code_div").length != 0) {
      $("#top_bar").hide(); // Hide Top Bar
      $.fn.loadAttendanceControlInfo(); // Load Attendance Control Share Info

      // Refreshing Page Every 5 Seconds
      if(reloader_variable == "") {
        $.fn.getQR();
        $.fn.getAttendingStudents();
        reloader_variable = setInterval(function() {
          $.fn.getQR();
          $.fn.getAttendingStudents();
        }, 5000);
      }
    }
    else {
      $("#top_bar").show(); // Displaying Top Bar

      //Stopping Refreshing Every 5 Seconds
      clearInterval(reloader_variable);
      reloader_variable = "";
    }
  });


  /*
  |---------------------------------------------------------------------------
  | Faculty Dashboard: Attendance Session
  |---------------------------------------------------------------------------
  |
  | This section contains functionalities related to the "Manage Departments"
  | section in the administrator navigation sidebar.
  |
  */


  // Closing Attendance Session
  $("#content").on("click", "#close_attendance_session_bt", function() {
    var url = "/terminate_attendance_session";
    var session_code = $('input[name="session_code"]').val();
    var params = "".concat("session_code=", session_code);
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      else {
        $.fn.facultyNav("navigation=fac_course");
      }
    }
    $.fn.postRequest(url, params, callback);
  });


  // Share Attendance Controls
  $("#content").on("click", "#share_control_bt", function() {
    var url = "/share_attendance_controls";
    var student_roll = $('input[name="student_roll"]').val();
    var class_codes = $("#class_code_div").text().trim();
    var session_code = $('input[name="session_code"]').val();
    var params = "".concat(
      "student_roll=", student_roll,
      "&class_codes=", class_codes,
      "&session_code=", session_code
    );
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      else {
        $('input[name="student_roll"]').val("")
        $.fn.loadAttendanceControlInfo();
        $.fn.getAttendingStudents();
      }
    }
    $.fn.postRequest(url, params, callback);
  });


  // Give Attendance to Student
  $("#content").on("click", "#give_attendance_bt", function() {
    var url = "/give_attendance"
    var student_roll = $('input[name="attendance_student_roll"]').val();
    var class_codes = $("#class_code_div").text().trim();
    var session_code = $('input[name="session_code"]').val();
    var params = "".concat(
      "student_roll=", student_roll,
      "&class_codes=", class_codes,
      "&session_code=", session_code
    );
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      else {
        $.fn.getAttendingStudents();
      }
    }
    $.fn.postRequest(url, params, callback);
    $('input[name="attendance_student_roll"]').val("");
  });


  // Function to load attendance control share info
  $.fn.loadAttendanceControlInfo = function() {
    var url = "/attendance_control";
    var params = {'session_code': $('input[name="session_code"]').val()};
    $("#control_share_desc").load(url, params);
  }


  // Function to load attending student info
  $.fn.getAttendingStudents = function() {
    var url = "/get_attending_students_stats";
    var session_code = $('input[name="session_code"]').val();
    var params = {'session_code': session_code};
    $("#attending_students_stats").load(url, params);

    url = "/get_attending_students_list";
    $("#attending_students_table_body").load(url, params);
  }


  // Function to load QRCode Image
  $.fn.getQR = function() {
    var url = "/gen_qr_timestamp";
    var session_code = $('input[name="session_code"]').val();
    var qr_timestamp = $('input[name="qr_timestamp"]').val();
    var params = "".concat("qr_timestamp=", qr_timestamp);

    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] == "S0") {
        qr_timestamp = res['qr_timestamp'];
        $('input[name="qr_timestamp"]').val(qr_timestamp);

        var url1 = "/gen_qr_img";
        var qrcode_id = "".concat(session_code, "_", qr_timestamp);
        var params1 = {'qrcode_id': qrcode_id}
        $("#qr_code_div").load(url1, params1); // Loading QR Image
      }
    }

    $.fn.postRequest(url, params, callback); // Obtaining QR Code ID
  }


  /*
  |---------------------------------------------------------------------------
  | Miscellaneous Events and Functions
  |---------------------------------------------------------------------------
  |
  | This section deals with miscellaneous events like navigating to sections,
  | logout handling, etc.
  |
  */


  // Start Session Button Click Event
  $("#content").on("click", ".session_bt", function() {
    var course_info = $(this).val()
    var params = "".concat("navigation=start_session&course_info=", course_info)
    $.fn.facultyNav(params);
  });


  /*
  * Function for Navigating Faculty Dashboard using Sidebar
  *
  * $.fn.facultyNav(params): takes one argument "params" to navigate faculty
  * dashboard to the section selected on the sidebar.
  *
  * Arguments
  * params: (String) takes the parameter in the form of "navigation=<section>".
  *
  * <section> is variable for the different sections defined as follows:
  * "fac_course" => Course Section
  * "fac_session" => Course Session Section
  * "fac_statistics" => Course Statistics Section
  * "start_session" => Start Session Section, takes additional course_info param
  *
  */
  $.fn.facultyNav = function(params) {
    var url = "/faculty_dash";
    var callback = function(responseText) {
      $("#content").html(responseText);
      $("#content").change();
    }
    $.fn.postRequest(url, params, callback);
  }


  // Navigating Sidebar
  $("#divNavBar .item").click(function() {
    switch(this.id) {
      case "faculty_course_bt":
        $.fn.facultyNav("navigation=fac_course");
        break;
      case "faculty_session_bt":
        $.fn.facultyNav("navigation=fac_session");
        break;
      case "faculty_course_statistics_bt":
        $.fn.facultyNav("navigation=fac_statistics");
        break;
      default:
        $.fn.facultyNav("navigation=fac_course");
    }
    $('.ui.sidebar').sidebar('toggle'); // Closing sidebar after click
  })


  // Logging Out
  $("#logout_bt").click(function() {
    $.fn.logOut();
  });


  //Loading Courses Page on Window Load
  $.fn.facultyNav("navigation=fac_course");

});
