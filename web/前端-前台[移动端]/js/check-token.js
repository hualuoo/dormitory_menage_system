var cache_token = "";
var username = "";
if(localStorage.getItem("cache_token") != null) {
	cache_token = localStorage.getItem("cache_token");
}

if(cache_token == "") {
	layer.open({
		content: '检测到您未登录，正在跳转到登录页面',
		skin: 'msg',
		time: 2 //2秒后自动关闭
	});
	setTimeout(function() {
		location.href = "login.html";
	}, 1000);
} else {
	$.ajax({
		url: "http://s1.mc.fyi:11453/token-verify/",
		type: "post",
		async: false,
		dataType: "json",
		data: {
			"token": cache_token
		},
		success: function(data) {
			username = data.username;
		},
		error: function(jqXHR) {
			localStorage.removeItem("cache_token");
			layer.open({
				content: '检测到您未登录，正在跳转到登录页面',
				skin: 'msg',
				time: 2 //2秒后自动关闭
			});
			setTimeout(function() {
				location.href = "login.html";
			}, 1000);
		}
	})
}