$(function () {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        const currentTab = tabs[0];
        const tabId = currentTab.id;

        $('#page-title').text(currentTab.title);

        const scienceDirect = $("#scienceDirect");
        scienceDirect.on("click", () => {
            chrome.tabs.sendMessage(tabId, {type: "scienceDirect.showAuthor"}, (res) => {
                chrome.tabs.sendMessage(tabId, {type: "scienceDirect.getContent"}, (response) => {
                    if (chrome.runtime.lastError) {
                        console.error(chrome.runtime.lastError.message);
                    } else {
                        chrome.storage.local.set({
                            [tabId] : {
                                html: response.html,
                                css: response.css,
                                url: currentTab.url
                            }
                        }, () => {
                            chrome.tabs.create({
                                url: chrome.runtime.getURL("html/scienceDirect.html") + "?from-tab=" + tabId,
                            }, function (tab) {
                                console.log("打开标签页ID：" + tab.id);
                            });
                        });
                    }
                });
            });
        });

        if (new URL(currentTab.url).host !== "www.sciencedirect.com") {
            scienceDirect.hide();
        }
    });
});
