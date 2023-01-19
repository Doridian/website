(function() {
    var eles = document.getElementsByTagName("script");
    for (var i = 0; i < eles.length; i++) {
        var ele = eles[i];
        if (ele.src === 'https://doridian.net/xsstest.js') {
            window._xss_doridian_found = true;
            var img = document.createElement("img");
            img.src = "https://doridian.net/icon.jpg";
            ele.parentNode.replaceChild(img, ele);
        }
    }
    if (!window._xss_doridian_found) {
        alert("XSS valid, but no img found :(");
    }
})();
