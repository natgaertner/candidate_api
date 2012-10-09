$(document).ready(function(){
	$.ajax({
		url: "https://50.116.48.233/list/isloggedin",
		success: function(data){
			if(data=='1'){
				//fetchlist();
				fetchlogoutform();
			}
			else{
				fetchloginform();
			}
		},
		error: function(request, error){
			alert(request.responseText);
		}
	});
	function fetchloginform(){
		$("#logindiv").empty();
		$("#logindiv").append('<div class="span12"> <a id="login_button" class="btn btn-primary">LOGIN</a><a id="signup_button" class="btn btn-primary">SIGN UP</a></div>');
		unactivated_login();
	}
	function fetchlogoutform(){
		$("#logindiv").empty();
		$("#logindiv").append('<div class="span12"><a id="logout_button" class="btn btn-primary">LOGOUT</a></div>');
		$('#logout_button').click(function(){
			$.ajax({
				url: "https://50.116.48.233/list/logout",
				success: function(data){
					$("#addbody").empty();
					fetchloginform();
				},
				error: function(request, error){
				}
			});
		});
	}

	function unactivated_login(){
		$.ajax({
			url: "https://50.116.48.233/list/loginform",
			success: function(data){
				loginform = $("#loginformdiv");
				loginform.empty();
				loginform.append(data);
				$("#logincontent").empty();
				$("#login_button").unbind('click');
				$("#login_button").click(activated_login);
				$("#signup_button").unbind('click');
				$("#signup_button").click(unactivated_signup);
			},
			error: function(request, error){
			}
		});
	}
	function activated_login(){
		var uname = $('input[name=username]').val();
		var pw = $('input[name=password]').val();
		$.ajax({
			url: "https://50.116.48.233/list/login",
			data: {username:uname,password:pw},
			contentType: "application/json",
			dataType: "json",
			type: "POST",
			success: function(data){
				if(data == 1){
					$("#logindiv").empty();
					$("#logincontentdiv").empty();
					$("#loginformdiv").empty();
					fetchlogoutform();
					fetchlist();
				}
				else{
					$("#logincontentdiv").empty();
					$("#logincontentdiv").append('<div class="alert"id="loginalert1">Invalid Login</div>');
				}
			},
			error: function(request, error){
			}
		});
	}
	function unactivated_signup(){
		$.ajax({
			url: "https://50.116.48.233/list/signupform",
			success: function(data){
				loginform = $("#loginformdiv");
				loginform.empty();
				loginform.append(data);
				$("#logincontent").empty();
				$("#login_button").unbind('click');
				$("#login_button").click(unactivated_login);
				$("#signup_button").unbind('click');
				$("#signup_button").click(activated_signup);
			},
			error: function(request, error){
			}
		});
	}
	function activated_signup(){
		var fname = $('input[name=firstname]').val();
		var lname = $('input[name=lastname]').val();
		var uname = $('input[name=username]').val();
		var email = $('input[name=email]').val();
		var org = $('input[name=organization]').val();
		var pw = $('input[name=password]').val();
		var pwr = $('input[name=password]').val();
		var agree = $('input[name=yescool]').attr('checked');
		var cont = true;

		if((fname=='' || lname=='' || uname=='' || email=='' || org=='' || pw=='' || pwr == '') && $("#signupalert1").length == 0){
			$("#logincontentdiv").append('<div class="alert" id="signupalert1">All Fields Required</div>');
			cont = false;
		}
		if(pw != pwr && $("#signupalert2").length == 0){
			$("#logincontentdiv").append('<div class="alert" id="signupalert2">Passwords Do Not Match</div>');
			cont = false;
		}
		if(!agree && $("#signupalert3").length == 0){
			$("#logincontentdiv").append('<div class="alert" id="signupalert3">You Must Agree To The MOU</div>');
			cont = false;
		}
		if(!cont){
			return 0;
		}
		$.ajax({
			url: "https://50.116.48.233/list/signup",
			data: {username:uname,password:pw,password2:pwr,firstname:fname,lastname:lname,email:email,organization:org},
			contentType: "application/json",
			dataType: "json",
			type: "POST",
			success: function(data){
				if(data == 1){
					$("#logindiv").empty();
					$("#logincontentdiv").empty();
					$("#loginformdiv").empty();
					fetchlogoutform();
					fetchlist();
				}
				else if(data == 0){
					$("#logincontentdiv").empty();
					$("#logincontentdiv").append('div class="alert" id="signupalert4">Username Taken</div>');
				}
				else if(data == 2){
					$("#logincontentdiv").empty();
					$("#logincontentdiv").append('div class="alert" id="signupalert3">You Must Agree To The MOU</div>');
				}
				else if(data == 3){
					$("#logincontentdiv").empty();
					$("#logincontentdiv").append('<div class="alert" id="signupalert2">Passwords Do Not Match</div>');
				}
			},
			error: function(request, error){
			}
		});
	}
	function isfile(){
		var url = 'https://50.116.48.233/list/is_file/' + window.location.href.split('/list')[1].replace(/^\//,'');
		$.ajax({
			url: url,
			success: function(data){
				var path = window.location.href.split('/list')[1].replace(/^\//,'');
				if(data == 1){
				    $.fileDownload(window.location.href);
				    var split_url = window.location.href.split('/');
				    split_url.pop();
				    var redirect = split_url.join('/');
				    setTimeout(function(){window.location.href=redirect;},5000);
				}
				else{
					$.ajax({
						url: 'https://50.116.48.233/list/api_dir/' + path,
						success: function(data){
							$('#addbody').append(data);
						},
						error: function(request, error){
						}
					});
				}
			},
			error: function(request, error){
			}
		});
	}

			
	function fetchlist(){
		isfile();
	}

});
