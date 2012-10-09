$(document).ready(function(){
	$.ajax({
		url: "https://50.116.48.233/list/isloggedin",
		success: function(data){
			if(data=='1'){
				fetchchangepwform();
			}
			else{
				$("#passwordchangediv").append('<div id="notloggedin" class="alert"><p>Not Logged In</p></div>');
				setTimeout(function(){window.location = '/list';}, 500);
			}
		},
		error: function(request, error){
			alert(request.responseText);
		}
	});
    function fetchchangepwform(){
	$.ajax({
		url: "https://50.116.48.233/list/changepass_form",
		success: function(data){
		    $("#passwordchangediv").append(data);
		    setclick();
		},
		error: function(request, error){
			alert(request.responseText);
		}
	});
    }
    function setclick(){
	$("#changepass").click(function(){
		var old_pass = $("input[name=old_pass]").attr('value');
		var new_pass = $("input[name=new_pass]").attr('value');
		var new_pass2 = $("input[name=new_pass2]").attr('value');
		if(new_pass != new_pass2){
			pwmatch = $("#pwmatch");
			if(pwmatch.size() == 0){
				$("#passwordchangediv").append('<div id="pwmatch" class="alert"><p>Passwords do no match</p></div>');
			}
		}
		$.ajax({
			url: "https://50.116.48.233/list/changepass_func",
			data: {new_pass:new_pass,new_pass2:new_pass2,old_pass:old_pass},
			type: "POST",
			contentType: "application/json",
			dataType: "json",
			type: "POST",
			//contentType: "application/json",
			//processData: false,
			success: function(data) {
				if(data=='0'){
					$("#passwordchangediv").append('<div id="notloggedin" class="alert"><p>Not Logged In</p></div>');
					setTimeout(function(){window.location = '/list';}, 500);
				}
				else if(data=='2'){
				    alert('Somehow you have submitted unmatching passwords');
				}
				else if(data=='1'){
					$("#passwordchangediv").append('<div id="changed" class="alert"><p>Password Changed!</p></div>');
					setTimeout(function(){window.location = '/list';}, 500);
				}
				else{
					alert('bad password or username');
				}

			},
			error: function(request, error) {
			}
		});
	});
    }
});

