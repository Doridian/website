try {
	alert('Ohi :3');
} catch {}

try {
	console.log('Ohi :3');
} catch {}

(function() {
    const eles = document.getElementsByTagName("script");
    for (let i = 0; i < eles.length; i++) {
        const ele = eles[i];
        if (ele.src === 'https://doridian.net/xsstest.js') {
            window._xss_doridian_found = true;
            const img = document.createElement("img");
            img.src = "https://doridian.net/icon.jpg";
            ele.parentNode.replaceChild(img, ele);
        }
    }
    if (!window._xss_doridian_found) {
        alert("XSS valid, but no img found :(");
    }
})();
