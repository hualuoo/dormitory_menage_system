(function($) {
	//直接拓展$
	$.keyboard = function(options) {
		var defaults = {
			num: 6,
			title: "输入密码",
			msg: "正在验证密码",
			skin: '&nbsp;',
			links: '&nbsp;',
			callback: function(data) {}
		};
		var val = $.extend(defaults, options);

		if($("#keyboardstyle").length == 0) {
			$("body").append("<style id='keyboardstyle'>.keyboardBox *{margin:0;padding:0;box-sizing:border-box}.keyboardBox{position:fixed;left:0;top:0;bottom:0;right:0;z-index:99999}.keyboardBox .background{position:absolute;left:0;top:0;width:100%;height:100%; background:rgba(0,0,0,.5)}.keyboardBox .box{text-align:center;height:350px;position:absolute;width:100%;bottom:-350px;left:0;background:#F7F7F7}.keyboardBox .box .title{height:45px;font-weight:700;font-size:16px;line-height:45px;border-bottom:1px solid #D9D9D9}.keyboardBox .box .title img{vertical-align:middle;padding-right:5px;margin-top:-3px}.keyboardBox .links,.keyboardBox .tip{ option:0; padding:0 10%;height:30px;line-height:30px;font-size:12px;text-align:left;color:red}.keyboardBox .links{text-align:right;color:#ccc}.keyboardBox .links a{color:#ccc}.keyboardBox .content{padding:0 10%}.keyboardBox .content ul{border-radius:4px;border:1px solid #D9D9D9;text-align:center;font-size:14px;background:#fff;height:40px;line-height:40px}.keyboardBox .content li{width:calc(100% / 6);float:left;border-left:1px solid #F1F1F1;height:40px}.keyboardBox .content li:first-child{border:none}.keyboardBox .numList{height:200px;background:#fff;border-top:2px solid #f1f1f1}.keyboardBox .numList li{width:calc(100% / 3);float:left;height:50px;line-height:50px;border-bottom:1px solid #F1F1F1;border-left:1px solid #F1F1F1;font-size:16px}.keyboardBox .numList li:active{background:#e9e9e9}.keyboardBox .numList li:nth-child(3n+1){border-left:none;cursor:pointer}.keyboardBox .cancel,.keyboardBox .delete{background:#F7F7F7}.keyboardBox .submitmsg{position:absolute;left:0;top:0;width:100%;height:100%;font-size:14px;text-align:center;display:none;vertical-align:middle}.keyboardBox .submitmsg span{display:table-cell;line-height:20px;vertical-align:middle}.keyboardBox .submitmsg font{padding:13px 26px;background:rgba(0,0,0,.8);border-radius:5px;color:#fff}.keyboardBox .submitmsg img{height:26px;vertical-align:middle;margin-right:6px}</style>");
		}
		
		var html = "<div class='keyboardBox'>";
		html += "	<div class='background'></div>";
		html += "	<div class='box'>";
		html += "	<div class='title'><img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6REU1MjZGOTFEOThGMTFFN0JENjhENzM1QzI5NjA0NjUiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6REU1MjZGOTJEOThGMTFFN0JENjhENzM1QzI5NjA0NjUiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpERTUyNkY4RkQ5OEYxMUU3QkQ2OEQ3MzVDMjk2MDQ2NSIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpERTUyNkY5MEQ5OEYxMUU3QkQ2OEQ3MzVDMjk2MDQ2NSIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Pg/Qc2QAAALdSURBVHjaTFNLSFRRGP7OPXceOjpK2Yxi9JAKyQrpATItiojKiggDA4VESiKxRbRp08IIoQe2CMoWQSKELgpCFCxqUbRJtIWYGZMuIksrB3NmnJk7956+cyezA2ce//99///9jyMwXAM4BqB4hQJ/SNhmNQy7joatENokPkLhCf3vabOhYRrLa2L5aKAjjtLYCOmUEzRAZj/J9DirYKgbcOQMgb20D6zQhmvCVLCJCtpJVAwwyCTTyHj30ttKjGSwLnisNzCc9VR3BJapGLCD2KjAu0g/A+wksA9eaxBZs5FKDvN/2T91MHSuWZjpl5DWY2R9EeJaqGTMhC1i9L+GR44ijR4iS9163H5orh/I/NQ3DN+GBkjfMfhUK5TzAo4SBoHzvDHWuZHfpdAl64RwcuT0DEIqg8jq/fAbDKqsIihVwR/kYF633mCNBhybDKl0yUh9I3EWWJpi5jncrbyDtzt6sM4XyqlRxCoNFMJYmYJudorEr+jcfA3dlZ0QTgaPqh6gvuQQrn65j0/xCcAs/juy3DFzWvVkhakHDjvlus+ETqC2OII13hJcmOpA1+frQKCKjAC9meWlcQOYbgBbJSHp9Jfh0ngrbDuBy2vPoS3ajq7pW0Bhda4nymJKfhgOF0pIk/MPsikhjucpbGMMRnA7AhW4MnUTPXPPMBkfB4IkCw+JWXAPJiGSo8y7j0sbkzhfruUXUtE2BBfvIS1PMYjpGBKzyShHXs7MXhJtXbqF8PcWZD21sHwJyOyQwMhuXXoRrLznKFjs5V5MIBnohiFCuXeg3A5x2X6hIN4MM1uBjNkEf+ogbe4YdVcX+HhOY6GoAZYnAl/6OOsccsnuMjmvkLd0kuu9Cz/CTUxYT5veH7JH9rjNpyw9yiAt3ZxLkPJus94t7rxNO0r7Ra5vAlnZjPx4DPkJliX/e43uUb/5SOoo8SwXqo2kD7lXKg/wffRR5cPcsq2cPwIMANFGI8sktpyZAAAAAElFTkSuQmCC'/>" + val.title + "</div>";
		html += "	<div class='tip'></div>";
		html += "	<div class='content'><ul>";
		for(i = 0; i < val.num; i++) {
			html += "	<li><span></span></li>";
		}
		html += "	</ul></div>";
		html += "	<div class='links'>" + val.links + "</div>";
		html += "		<ul class='numList'>";
		html += "			<li class='n'>1</li><li class='n'>2</li><li class='n'>3</li><li class='n'>4</li><li class='n'>5</li><li class='n'>6</li><li class='n'>7</li><li class='n'>8</li><li class='n'>9</li><li class='cancel'>取消</li><li class='n'>0</li><li class='delete'><img src='data:image/png;base64,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'/></li>";
		html += "		</ul>";
		html += "	</div>";
		html += "	<div class='submitmsg'><span><font><img src='data:image/gif;base64,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'>" + val.msg + "</font></span></div>";
		html += "</div>";
		//创建键盘对象，并暴露方法给调用对象。
		var obj = {};
		var dom = $(html);
		var nowNo = 0;
		var calldata = [];
		obj.showKeyBoard = function() {
			if($(".keyboardBox").length == 0) {
				$("body").append(dom);
				$(".keyboardBox .content li").css({'width':'calc(100% / '+ val.num +')'});
				dom.find(".background").fadeIn();
				dom.children(".box").animate({
					'bottom': '0'
				}, 150);
				nowNo = 0;
				dom.find('.content').find('span').text(' ');
			};
		};
		obj.reset = function(msg) {
			nowNo = 0;
			dom.find('.content').find('span').text("");
			dom.find('.submitmsg').css({
				"display": "none"
			});
			if(msg) {
				dom.find('.tip').text(msg);
			} else {
				dom.find('.tip').text('');
			}
			calldata = [];
		}
		obj.hideKeyBoard = function() {
			if($(".keyboardBox").length != 0) {
				dom.children(".box").animate({
					'bottom': '-360px'
				}, 150)
				$(".keyboardBox").find(".background").fadeOut(function() {
					$(".keyboardBox").remove();
				});
				obj.reset();
			}
		}
		dom.find(".background").click(function() {
			if(nowNo <= val.num) {
				obj.hideKeyBoard();
			}
		});
		dom.find('li').click(function() {
			if(nowNo <= val.num && nowNo > -1) {
				if($(this).hasClass('cancel')) {
					obj.hideKeyBoard();
				} else if($(this).hasClass('delete')) {
					if(nowNo > 0) {
						nowNo--;
						dom.find('.content').find('span').eq(nowNo).text("");
						calldata.pop();
					}
				} else if($(this).hasClass('n')) {
					dom.find('.tip').text(''); //清空提示
					dom.find('.content').find('span').eq(nowNo).text("●");
					calldata.push($(this).text());
					nowNo++;
					if(nowNo == val.num) {
						dom.find('.submitmsg').css({
							"display": "table"
						});
						val.callback(calldata);
					}
				}
			} else {
				return false;
			}
		})
		return obj;
	};
})(window.Zepto || window.jQuery);