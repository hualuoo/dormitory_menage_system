(function($) {
	$.fn.myflow = function(options) {
		var defaults = {
			url: '',
			type: 'post',
			data: {},
			clearlist: false,
			colspan: 4,
			template: function(data) {
				console.log(data);
				return "<div>请添加模板！</div>";
			},
			dataArr: function(data) {
				return data;
			}
		};
		var val = $.extend(defaults, options);
		//生成子列
		if(this.children().length == 0) {
			var thisHtml = '';
			for(i = 0; i < val.colspan; i++) {
				thisHtml += "<div class='ui-myflow-item'></div>";
			}
			this.addClass("clearfix");
			this.html(thisHtml).children().css({
				"width": 10 / val.colspan * 10 + "%",
				"float": "left"
			});
		}
		if(val.clearlist) {
			this.children().html("");
		}
		//获取数据
		var children = this.children();
		$.ajax({
			url: val.url,
			type: val.post,
			data: val.data,
			dataType: "json",
			success: function(data) {
				var newData = val.dataArr(data);
				console.log(newData)
				for(i = 0; i < newData.length; i++) {
					var heightArr = [];
					children.each(function() {
						heightArr.push($(this).height());
					});
					var index = heightArr.indexOf(Math.min.apply(null, heightArr));
					var items = $(val.template(newData[i])).css({
						'opacity': '0'
					})
					children.eq(index).append(items);
					items.animate({
						'opacity': '1'
					});
				}
			},
			error: function(XMLHttpRequest, textStatus, errorThrown) {
				console.log(XMLHttpRequest.status + "" + XMLHttpRequest.readyState + "" + errorThrown);
			}
		});
	};
})(window.Zepto || window.jQuery);