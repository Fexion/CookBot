$(function(){
	$('button').click(function(){
		var text = $('#userInput').val();
    console.log(text);
    var list = document.getElementById('msgHistory');
    var line = document.createElement('tr');
    var entry = document.createElement('div');
    entry.className = 'userMsg Msg';
    entry.appendChild(document.createTextNode(text));
    line.appendChild(entry);
    list.appendChild(line);
    document.getElementById('userInput').value = '';
    var objDiv = document.getElementById("chat_window");
    objDiv.scrollTop = objDiv.scrollHeight;

		$.ajax({
			url: '/processM',
			data: {'user_text': text},
			type: 'POST',
			success: function(response){
				console.log(response);
        var list = document.getElementById('msgHistory');
        var line = document.createElement('tr');
        var entry = document.createElement('div');
        entry.className = 'botMsg Msg';
        entry.innerHTML = response;
        line.appendChild(entry);
        list.appendChild(line);
        var objDiv = document.getElementById("chat_window");
        objDiv.scrollTop = objDiv.scrollHeight;
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
