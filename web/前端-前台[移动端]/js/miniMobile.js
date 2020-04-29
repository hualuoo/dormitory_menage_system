/* 
 * minimobile.js v0.0.1 by chenyaowen 
 * 在保留作者签名的情况下，允许使用与商业用途
 */
 if(!window.Zepto && !window.jQuery){
    console.log("minimobile 是基于Zepto.js 或者 jQuery.js 的，请检查页面是否已在miniMobile之前引入！")
 }
;(function(win, lib) {
	//摘自淘宝移动端
    var doc = win.document;
    var docEl = doc.documentElement;
    var metaEl = doc.querySelector('meta[name="viewport"]');
    var flexibleEl = doc.querySelector('meta[name="flexible"]');
    var dpr = 0;
    var scale = 0;
    var tid;
    var flexible = lib.flexible || (lib.flexible = {});
    var designPixel = 750;//设计稿件尺寸
    
    if (metaEl) { 
        console.warn('将根据已有的meta标签来设置缩放比例');       
        var match = metaEl.getAttribute('content').match(/initial\-scale=([\d\.]+)/);
        if (match) {
            scale = parseFloat(match[1]);
            dpr = parseInt(1 / scale);
        }
    } else if (flexibleEl) {
        var content = flexibleEl.getAttribute('content');
        if (content) {
            var initialDpr = content.match(/initial\-dpr=([\d\.]+)/);
            var maximumDpr = content.match(/maximum\-dpr=([\d\.]+)/);
            if (initialDpr) {
                dpr = parseFloat(initialDpr[1]);
                scale = parseFloat((1 / dpr).toFixed(2));    
            }
            if (maximumDpr) {
                dpr = parseFloat(maximumDpr[1]);
                scale = parseFloat((1 / dpr).toFixed(2));    
            }
        }
    }
    if (!dpr && !scale) {
        var isAndroid = win.navigator.appVersion.match(/android/gi);
        var isIPhone = win.navigator.appVersion.match(/iphone/gi);
        var devicePixelRatio = win.devicePixelRatio;
        if (isIPhone) {            
            if (devicePixelRatio >= 3 && (!dpr || dpr >= 3)) {                
                dpr = 3;
            } else if (devicePixelRatio >= 2 && (!dpr || dpr >= 2)){
                dpr = 2;
            } else {
                dpr = 1;
            }
        } else {            
            dpr = 1;
        }
        scale = 1 / dpr;
    }

    docEl.setAttribute('data-dpr', dpr);
    if (!metaEl) {
        metaEl = doc.createElement('meta');
        metaEl.setAttribute('name', 'viewport');
        metaEl.setAttribute('content', 'initial-scale=' + scale + ', maximum-scale=' + scale + ', minimum-scale=' + scale + ', user-scalable=no');
        if (docEl.firstElementChild) {
            docEl.firstElementChild.appendChild(metaEl);
        } else {
            var wrap = doc.createElement('div');
            wrap.appendChild(metaEl);
            doc.write(wrap.innerHTML);
        }
    }

    function refreshRem(){
        var width = docEl.getBoundingClientRect().width;
        if (width / dpr > designPixel) {    //如果分辨率不是1，那么获取的物理宽度应该乘以分辨率，才是最终可用的width
            width = width * dpr;
        }
        var rem = width / (designPixel/100); //计算最终还原到设计图上的比例，从而设置到文档上
        docEl.style.fontSize = rem + 'px';
        flexible.rem = win.rem = rem;
    }

    win.addEventListener('resize', function() {
        clearTimeout(tid);
        tid = setTimeout(refreshRem, 300);
    }, false);
    win.addEventListener('pageshow', function(e) {
        if (e.persisted) {
            clearTimeout(tid);
            tid = setTimeout(refreshRem, 300);
        }
    }, false);

    if (doc.readyState === 'complete') {
        doc.body.style.fontSize = 16 * dpr + 'px';
    } else {
        doc.addEventListener('DOMContentLoaded', function(e) {
            doc.body.style.fontSize = 16 * dpr + 'px';
        }, false);
    }
    refreshRem();

    flexible.dpr = win.dpr = dpr;
    flexible.refreshRem = refreshRem;
    flexible.rem2px = function(d) {
        var val = parseFloat(d) * this.rem;
        if (typeof d === 'string' && d.match(/rem$/)) {
            val += 'px';
        }
        return val;
    }
    flexible.px2rem = function(d) {
        var val = parseFloat(d) / this.rem;
        if (typeof d === 'string' && d.match(/px$/)) {
            val += 'rem';
        }
        return val;
    }

})(window, window['lib'] || (window['lib'] = {}));
/*
 * asideUi 侧栏
 */
;
(function($) {
	$.fn.asideUi = function(options) {
		var defaults = {
			size: '100%',
			hasmask: true,
			position: 'left',
			sidertime: 300
		};
		var val = $.extend(defaults, options);
		var obj = function() {},
			_self = this,
			thisMask = $("<div class='ui-aside-mask'></div>"),
			thisCss = {},
			thisCss2 = {};
		thisCss[val.position] = '-' + val.size;
		this.css({
			'top': (val.position == "bottom") ? "auto" : 0,
			'bottom': 0
		});
		thisCss2[val.position] = 0;
		_self.css(thisCss);
		
		obj.toggle = function() {
			if(_self.hasClass('ui-aside-open')) {
				_self.removeClass('ui-aside-open');
				_self.animate(thisCss, val.sidertime);
				$('.ui-aside-mask').animate({
					'opacity': 0
				}, 100, function() {
					$(this).remove();
				});
			} else {
				_self.addClass('ui-aside-open');
				_self.animate(thisCss2, val.sidertime);
				if(val.hasmask) {
					$('body').append(thisMask);
					$(".ui-aside-mask").animate({
						'opacity': 1
					}, 100);
				}
			}
		}
		thisMask.tap(function() {
			obj.toggle();
		})
		return obj;
	};
})(window.Zepto || window.jQuery)
/*
 * 返回顶部
 */
function goTop(acceleration, time) {
	acceleration = acceleration || 0.1;
	time = time || 16;
	var x1 = 0;
	var y1 = 0;
	var x2 = 0;
	var y2 = 0;
	var x3 = 0;
	var y3 = 0;
	if(document.documentElement) {
		x1 = document.documentElement.scrollLeft || 0;
		y1 = document.documentElement.scrollTop || 0;
	}
	if(document.body) {
		x2 = document.body.scrollLeft || 0;
		y2 = document.body.scrollTop || 0;
	}
	var x3 = window.scrollX || 0;
	var y3 = window.scrollY || 0;
	// 滚动条到页面顶部的水平距离
	var x = Math.max(x1, Math.max(x2, x3));
	// 滚动条到页面顶部的垂直距离
	var y = Math.max(y1, Math.max(y2, y3));
	// 滚动距离 = 目前距离 / 速度, 因为距离原来越小, 速度是大于 1 的数, 所以滚动距离会越来越小
	var speed = 1 + acceleration;
	window.scrollTo(Math.floor(x / speed), Math.floor(y / speed));
	// 如果距离不为零, 继续调用迭代本函数
	if(x > 0 || y > 0) {
		var invokeFunction = "goTop(" + acceleration + ", " + time + ")";
		window.setTimeout(invokeFunction, time);
	}
}

/*
 * ui-progress进度条
 */
;
(function($) {
	$.fn.progressUi = function(options) {
		var defaults = {
			skin: ''
		};
		var val = $.extend(defaults, options);
		var attrs = {
				max: this.attr('max') || 0,
				value: this.attr("value") || 0
			},
			doms = $('<div class="ui-progressBox"></div>');
		domsContent = $('<div class="progress-content ' + val.skin + '"></div>');
		this.wrap(doms);
		domsContent.animate({
			'width': attrs.value / attrs.max * 100 + '%',
		});
		doms.prepend(domsContent);
	};
})(window.Zepto || window.jQuery)