// timer = setInterval(()=>{window.scrollTo(0, document.body.scrollHeight)}, 3000)
// clearInterval(timer)

var urls = new Set();
var a_elements = document.querySelectorAll('a[href*="/video/"]')
for (element of a_elements){
    var href = element.getAttribute('href');
    if (href.includes("@") && href.includes("tiktok.com")){
        urls.add(href);
    }
}
[...urls]
