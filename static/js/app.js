$(document).ready(function(){
	function updateView(candidates){
		var table=$("#resultTable tbody");
		table.html('');
		$.each(candidates, function(index, value){
			var trE1=$('<tr><td>'+value.uid+'</td><td>'+value.state+'</td><td>'+value.office_level+'</td><td>'+value.electoral_district+'</td><td>'+value.office_name+'</td><td>'+value.candidate_name+'</td><td>'+value.candidate_party+'</td><td>'+value.completed+'</td><td>'+value.incumbent+'</td><td>'+value.phone+'</td><td>'+value.mailing_address+'</td><td>'+value.website+'</td><td>'+value.email+'</td><td>'+value.facebook_url+'</td><td>'+value.twitter_name+'</td><td>'+value.google_plus+'</td><td>'+value.wiki_word+'</td><td>'+value.youtube+'</td></tr>');
			table.append(trE1);
		});
		$("#resultTable").tablesorter();
	}
	$("#send").click(function(){
		var state = $("input[name=state]").attr('value');
		var office_level = $("input[name=office_level]").attr('value');
		var electoral_district = $("input[name=electoral_district]").attr('value');
		var office_name = $("input[name=office_name]").attr('value');
		var candidate_name = $("input[name=candidate_name]").attr('value');
		var candidate_party = $("input[name=candidate_party]").attr('value');
		//console.log(state);
		//console.log(office_level);
		//console.log(electoral_district);
		//console.log(office_name);
		//console.log(candidate_name);
		//console.log(candidate_party);
		var p = {state : state, office_level : office_level, electoral_district : electoral_district, office_name : office_name, candidate_name : candidate_name, candidate_party : candidate_party}
		$.ajax({
			url: "https://50.116.48.233/api/candidates",
			data: p,
			contentType: "application/json",
			dataType: "json",
			success: function(data) {
				//console.log("get");
				updateView(data);
			},
			error: function(request, error) {
				alert(request.responseText);
				//console.log("error");
			}
		});
	});
});
