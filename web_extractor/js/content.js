chrome.runtime.onConnect.addListener((port) => {
    console.info('content.js onConnect', port)
});

// 监听background页面发来的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.info("content.js 接收到消息：", request);

    switch (request.type) {
        case "scienceDirect.showAuthor":
            if (!$("article .Banner>.wrapper>p:nth-of-type(2)").length) {
                $("#show-more-btn").click();
                sendResponse("show");
            } else {
                sendResponse("shown");
            }
            break;
        case "scienceDirect.getContent":
            sendResponse({
                html: $("article").html(),
                css: $('link[rel="stylesheet"][href*="arp.css"]').attr("href")
            });
            break;
    }
});
