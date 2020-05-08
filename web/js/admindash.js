$(document).ready(function() {

  /*
  |---------------------------------------------------------------------------
  | UI Toggles
  |---------------------------------------------------------------------------
  |
  | This section contains all UI toggle actions like sidebars and popups.
  |
  */


  // Sidebar Toggle
  $("#sidebar_toggle_bt").click(function() {
    $('.ui.sidebar').sidebar('toggle');
  });


  // Popup and Sidebar Toggle
  $(document).on("change", "#content", function() {
    $("button").popup();
    $('.ui.dropdown').dropdown();
  });



  /*
  * TODO: Add Modify Button Functionality
  * TODO: Add Delete Button Functionality
  */

  /*
  |---------------------------------------------------------------------------
  | Administrator Dashboard: Manage Departments
  |---------------------------------------------------------------------------
  |
  | This section contains functionalities related to the "Manage Departments"
  | section in the administrator navigation sidebar.
  |
  */


  // Adding a Department
  $('#content').on('click', '#btnAddDept', function() {
    var url = "/insert_dept";
    var dept_name = $('input[name="dept-name"]').val();
    var dept_code = $('input[name="dept-code"]').val();
    var params = "".concat("dept_name=", dept_name, "&dept_code=", dept_code);
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      $.fn.adminNav("navigation=dept"); // Reloading section
    }
    $.fn.postRequest(url, params, callback); // Adding a department
  });


  //Adding Departments from CSV
  $("#content").on("click", "#btnAddDeptCSV", function() {
    var fileElem = document.getElementById("selectDeptCSV");
    fileElem.click();
    fileElem.onchange = function() {
      var CSVFile = fileElem.files[0];
      if(CSVFile != null) {
        var fileReader = new FileReader();
        fileReader.onload = function(event) {
          var url = "/insert_dept_csv";
          var params = "".concat("dept_csv=", event.target.result);
          var callback = function(responseText) {
            var res = JSON.parse(responseText);
            if(res['status'] == "S2") {
              alert(res['message'] + '\n\nERROR:\n' + res['fail_data']);
            }
            else if(res['status'] != "S0") {
              alert(res['message']);
            }
            $.fn.adminNav("navigation=dept"); // Reloading section
          }
          $.fn.postRequest(url, params, callback); // Adding departments
        }
        fileReader.readAsText(CSVFile, "UTF-8");
      }
    };
  });


  // Download CSV Sample for Adding Departments
  $("#content").on("click", "#btnAddDeptCSVSample", function() {
    window.location.href="csv_samples/dept_sample.csv";
  });


  /*
  |---------------------------------------------------------------------------
  | Administrator Dashboard: Manage Faculties
  |---------------------------------------------------------------------------
  |
  | This section contains functionalities related to the "Manage Faculties"
  | section in the administrator navigation sidebar.
  |
  */


  // Adding a Faculty
  $('#content').on('click', '#add_faculty_bt', function() {
    var url = "/insert_faculty";
    var faculty_name = $('input[name="faculty_name"]').val();
    var faculty_code = $('input[name="faculty_code"]').val();
    var faculty_dept = $('input[name="faculty_dept"]').val();
    var faculty_pwd = $('input[name="faculty_pwd"]').val();
    var faculty_pwd_cnf = $('input[name="faculty_pwd_cnf"]').val();
    var params = "".concat(
      "faculty_name=", faculty_name,
      "&faculty_code=", faculty_code,
      "&faculty_dept=", faculty_dept,
      "&faculty_pwd=", faculty_pwd,
      "&faculty_pwd_cnf=", faculty_pwd_cnf
    );
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      $.fn.adminNav("navigation=faculty"); // Reloading section
    }
    $.fn.postRequest(url, params, callback); // Adding a faculty
  });


  //Adding Faculties from CSV
  $("#content").on("click", "#add_faculty_csv_bt", function() {
    var fileElem = document.getElementById("add_faculty_csv_file");
    fileElem.click();
    fileElem.onchange = function() {
      var CSVFile = fileElem.files[0];
      if(CSVFile != null) {
        var fileReader = new FileReader();
        fileReader.onload = function(event) {
          var url = "/insert_faculty_csv";
          var params = "".concat("faculty_csv=", event.target.result);
          var callback = function(responseText) {
            var res = JSON.parse(responseText);
            if(res['status'] == "S2") {
              alert(res['message'] + '\n\nERROR:\n' + res['fail_data']);
            }
            else if(res['status'] != "S0") {
              alert(res['message']);
            }
            $.fn.adminNav("navigation=faculty"); // Reloading section
          }
          $.fn.postRequest(url, params, callback); // Adding departments
        }
        fileReader.readAsText(CSVFile, "UTF-8");
      }
    };
  });


  // Download CSV Sample for Adding Faculties
  $("#content").on("click", "#add_faculty_csv_sample_bt", function() {
    window.location.href="csv_samples/faculty_sample.csv";
  });


  /*
  |---------------------------------------------------------------------------
  | Administrator Dashboard: Manage Class Groups
  |---------------------------------------------------------------------------
  |
  | This section contains functionalities related to the "Manage Class Groups"
  | section in the administrator navigation sidebar.
  |
  */


  // Adding a Class Group
  $('#content').on('click', '#add_class_bt', function() {
    var url = "/insert_class";
    var class_dept = $('input[name="class_dept"]').val();
    var class_start = $('input[name="class_start_year"]').val();
    var class_end = $('input[name="class_graduating_year"]').val();
    var class_section = $('input[name="class_section"]').val();
    var params = "".concat(
      "dept_name=", class_dept,
      "&class_start=", class_start,
      "&class_end=", class_end,
      "&class_section=", class_section
    );
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      $.fn.adminNav("navigation=class"); // Reloading section
    }
    $.fn.postRequest(url, params, callback); // Adding a class group
  });


  //Adding Class Groups from CSV
  $("#content").on("click", "#add_class_csv_bt", function() {
    var fileElem = document.getElementById("add_class_csv_file");
    fileElem.click();
    fileElem.onchange = function() {
      var CSVFile = fileElem.files[0];
      if(CSVFile != null) {
        var fileReader = new FileReader();
        fileReader.onload = function(event) {
          var url = "/insert_class_csv";
          var params = "".concat("class_csv=", event.target.result);
          var callback = function(responseText) {
            var res = JSON.parse(responseText);
            if(res['status'] == "S2") {
              alert(res['message'] + '\n\nERROR:\n' + res['fail_data']);
            }
            else if(res['status'] != "S0") {
              alert(res['message']);
            }
            $.fn.adminNav("navigation=class"); // Reloading section
          }
          $.fn.postRequest(url, params, callback); // Adding departments
        }
        fileReader.readAsText(CSVFile, "UTF-8");
      }
    };
  });


  // Download CSV Sample for Adding Class Groups
  $("#content").on("click", "#add_class_csv_sample_bt", function() {
    window.location.href="csv_samples/class_sample.csv";
  });


  /*
  |---------------------------------------------------------------------------
  | Administrator Dashboard: Manage Students
  |---------------------------------------------------------------------------
  |
  | This section contains functionalities related to the "Manage Students"
  | section in the administrator navigation sidebar.
  |
  */


  // Adding a Student
  $('#content').on('click', '#add_student_bt', function() {
    var url = "/insert_student";
    var student_roll = $('input[name="student_roll"]').val();
    var student_name = $('input[name="student_name"]').val();
    var class_code = $('input[name="student_class_code"]').val();
    var params = "".concat(
      "student_roll=", student_roll,
      "&student_name=", student_name,
      "&class_code=", class_code
    );
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      $.fn.adminNav("navigation=student"); // Reloading section
    }
    $.fn.postRequest(url, params, callback); // Adding a class group
  });


  //Adding Students from CSV
  $("#content").on("click", "#add_student_csv_btn", function() {
    var fileElem = document.getElementById("add_student_csv_file");
    fileElem.click();
    fileElem.onchange = function() {
      var CSVFile = fileElem.files[0];
      if(CSVFile != null) {
        var fileReader = new FileReader();
        fileReader.onload = function(event) {
          var url = "/insert_student_csv";
          var params = "".concat("student_csv=", event.target.result);
          var callback = function(responseText) {
            var res = JSON.parse(responseText);
            if(res['status'] == "S2") {
              alert(res['message'] + '\n\nERROR:\n' + res['fail_data']);
            }
            else if(res['status'] != "S0") {
              alert(res['message']);
            }
            $.fn.adminNav("navigation=student"); // Reloading section
          }
          $.fn.postRequest(url, params, callback); // Adding departments
        }
        fileReader.readAsText(CSVFile, "UTF-8");
      }
    };
  });


  // Download CSV Sample for Adding Students
  $("#content").on("click", "#add_student_csv_sample_bt", function() {
    window.location.href="csv_samples/student_sample.csv";
  });


  // Unlink Device from Student
  $("#content").on("click", ".unlink_bt", function() {
    var url = "/unregister_device";
    var student_roll = $(this).val();
    var params = "".concat("student_roll=", student_roll);
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      $.fn.adminNav("navigation=student");
    }
    $.fn.postRequest(url, params, callback);
  })


  /*
  |---------------------------------------------------------------------------
  | Administrator Dashboard: Manage Courses
  |---------------------------------------------------------------------------
  |
  | This section contains functionalities related to the "Manage Courses"
  | section in the administrator navigation sidebar.
  |
  */


  // Adding a Course
  $('#content').on('click', '#add_course_bt', function() {
    var url = "/insert_course";
    var course_code = $('input[name="course_code"]').val();
    var course_name = $('input[name="course_name"]').val();
    var faculty_codes = $('input[name="course_faculty_code"]').val();
    var class_codes = $('input[name="course_class_code"]').val();
    var params = "".concat(
      "course_code=", course_code,
      "&course_name=", course_name,
      "&faculty_codes=", faculty_codes,
      "&class_codes=", class_codes
    );
    var callback = function(responseText) {
      var res = JSON.parse(responseText);
      if(res['status'] != "S0") {
        alert(res['message']);
      }
      $.fn.adminNav("navigation=course"); // Reloading section
    }
    $.fn.postRequest(url, params, callback); // Adding a class group
  });


  //Adding Courses from CSV
  $("#content").on("click", "#add_course_csv_bt", function() {
    var fileElem = document.getElementById("add_course_csv_file");
    fileElem.click();
    fileElem.onchange = function() {
      var CSVFile = fileElem.files[0];
      if(CSVFile != null) {
        var fileReader = new FileReader();
        fileReader.onload = function(event) {
          var url = "/insert_course_csv";
          var params = "".concat("course_csv=", event.target.result);
          var callback = function(responseText) {
            var res = JSON.parse(responseText);
            if(res['status'] == "S2") {
              alert(res['message'] + '\n\nERROR:\n' + res['fail_data']);
            }
            else if(res['status'] != "S0") {
              alert(res['message']);
            }
            $.fn.adminNav("navigation=course"); // Reloading section
          }
          $.fn.postRequest(url, params, callback); // Adding departments
        }
        fileReader.readAsText(CSVFile, "UTF-8");
      }
    };
  });


  // Download CSV Sample for Adding Courses
  $("#content").on("click", "#add_course_csv_sample_bt", function() {
    window.location.href="csv_samples/course_sample.csv";
  });


  /*
  |---------------------------------------------------------------------------
  | Miscellaneous Events and Functions
  |---------------------------------------------------------------------------
  |
  | This section deals with miscellaneous events like navigating to sections,
  | logout handling, etc.
  |
  */


  /*
  * Function for Navigating Administrator Dashboard using Sidebar
  *
  * $.fn.adminNav(params): takes one argument "params" to navigate admin
  * dashboard to the section selected on the sidebar.
  *
  * Arguments
  * params: (String) takes the parameter in the form of "navigation=<section>".
  *
  * <section> is variable for the different sections defined as follows:
  * "dept" => Manage Departments Section
  * "faculty" => Manage Faculties Section
  * "home" => Admin Dashboard Home
  * "class" => Manage Class Groups Section
  * "course" => Manage Courses Section
  * "student" => Manage Students Section
  *
  */
  $.fn.adminNav = function(params) {
    var url = "/admin_dash";
    var callback = function(responseText) {
      $("#content").html(responseText);
      $("#content").change();
    }
    $.fn.postRequest(url, params, callback);
  }


  // Navigating Sidebar
  $("#divNavBar .item").click(function() {
    switch(this.id) {
      case "manage_dept_bt":
        $.fn.adminNav("navigation=dept");
        break;
      case "manage_faculty_bt":
        $.fn.adminNav("navigation=faculty");
        break;
      case "manage_class_bt":
        $.fn.adminNav("navigation=class");
        break;
      case "manage_students_bt":
        $.fn.adminNav("navigation=student");
        break;
      case "manage_courses_bt":
        $.fn.adminNav("navigation=course");
        break;
      default:
        $.fn.adminNav("navigation=home");
    }
    $('.ui.sidebar').sidebar('toggle'); // Closing sidebar after click
  })


  // Logging Out
  $("#btnLogout").click(function() {
    $.fn.logOut();
  });

  // Navigating to Home on Load
  $.fn.adminNav("navigation=home");

});
