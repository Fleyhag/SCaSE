const selectorGenerator = new SelectorGenerator();

function htmlToTextWithNewlines(tempDiv) {
    $(".captions", tempDiv).remove();
    $("[caption]", tempDiv).each((i, caption) => {
        const c = $(caption);
        const cid = "{{" + c.attr("caption") + "$" + selectorGenerator.getSelector(caption) + "@" + c.attr("local-src") + "}}";
        c.parent().text(cid);
    });

    // 遍历所有子元素
    function getText(node, result = []) {
        if (node.nodeType === Node.TEXT_NODE) {
            // 如果是文本节点，直接添加到结果中
            result.push(node.textContent);
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // 如果是元素节点
            for (let i = 0; i < node.childNodes.length; i++) {
                getText(node.childNodes[i], result);
            }
            // 在某些块级元素后添加换行符
            if (['P', 'DIV', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'LI', 'FIGURE'].includes(node.tagName)) {
                result.push('\n');
            }
        }
        return result;
    }

    return getText(tempDiv).join('');
}

$(async () => {
    const queryParams = new URLSearchParams(window.location.search);
    const tabId = queryParams.get("from-tab");

    const result = await chrome.storage.local.get(tabId);
    console.info(result)
    const cssLink = $("<link/>").attr({
        rel: "stylesheet",
        type: "text/css",
        href: result[tabId]?.css,
    });
    $("head").prepend(cssLink);
    const article = $("#x-plugin-article");
    const toolbar = $("#x-plugin-tool");

    article.html(result[tabId]?.html);
    const paperTitle = $("#screen-reader-main-title", article).text();
    $("title").text(paperTitle);

    const paperId = $("#article-identifier-links a").attr("href").split('/').pop();

    // chrome.storage.local.remove(tabId).then(() => {
    //     console.info("storage clean: " + tabId);
    // });

    $(".Banner>button", article).remove();
    $(".Banner>.banner-options", article).remove();
    $(".Banner>.wrapper>p:nth-of-type(2)", article).remove();
    $(".Banner>.wrapper>button", article).remove();
    $("#issue-navigation", article).remove();
    // $(".author-highlights .list-label", article).remove();

    $("a", article).each((i, ele) => {
        const href = $(ele).attr("href");

        if (href.startsWith('/')) {
            $(ele).attr("href", "https://www.sciencedirect.com" + href);
        } else if (href.startsWith("#b") && $(ele).attr("data-xocs-content-type") === "reference") {
            $(ele).attr("href", href.replace("#b", "#ref-id-b"));
        }
    });

    $(".tables", article).each((i, ele) => {
        const caption = $(".captions", ele).text().replace(/Table\s+\d+.?\s+/, '').replace(/\.$/, '');
        $(".groups", ele).attr({
            "caption": caption,
            "index": i + 1
        });
    });

    let index = 1;
    $("figure", article).each((i, ele) => {
        if (!$(ele).find("figure").length) {
            const span_tags = $(">span", ele);
            const caption = $(".captions", ele).text().replace(/Figure\s+\d+.?\s+/, '').replace(/\.$/, '');

            for (const span of span_tags) {
                const img = $("img", span);
                const thumb = $(`li:nth-child(${$("li", span).length}) a`).attr("href");
                const origin = $("li:first a", span).attr("href");
                if (img.length && caption) {
                    img.attr({
                        "src": origin,
                        "caption": caption,
                        "index": index++,
                        "thumb-src": thumb
                    });
                    img.css("height", img.attr("height") + "px");

                    $("ol", span).remove();
                }
            }
        }
    });

    function clearClass() {
        $(".x-plugin-clicked").removeClass("x-plugin-clicked");
        $(".x-plugin-text-clicked").removeClass("x-plugin-text-clicked");
        toolbar.hide();
    }

    function showTool(rect) {
        const width = toolbar.width();
        toolbar.css("top", (rect.bottom + window.scrollY) + "px");
        if (rect.left + width >= window.innerWidth) {
            toolbar.css("left", (window.innerWidth - width - 60) + "px");
        } else {
            toolbar.css("left", rect.left + "px");
        }

        toolbar.show();
    }

    let mediaType;
    function selectType(target, type) {
        mediaType = type;

        article.off();

        if ($(target).hasClass("x-plugin-btn-selected")) {
            $(target).removeClass("x-plugin-btn-selected");
            clearClass();
            return false;
        } else {
            $(".x-plugin-btn-selected").removeClass("x-plugin-btn-selected");
            $(target).addClass("x-plugin-btn-selected");
            return true;
        }
    }

    $("#x-plugin-tableSelect").on("click", (evt) => {
        if (selectType(evt.target, "table")) {
            article.on("click", (e) => {
                clearClass();
                const table = $(e.target).parents(".tables");
                if (table.length) {
                    table.addClass("x-plugin-clicked");
                    showTool(table.get(0).getBoundingClientRect());
                }
            });
        }
    });

    $("#x-plugin-imageSelect").on("click", (evt) => {
        if (selectType(evt.target, "image")) {
            article.on("click", (e) => {
                clearClass();
                const figure = $(e.target).parents(".figure");
                if (figure.length) {
                    figure.addClass("x-plugin-clicked");
                    showTool(figure.get(0).getBoundingClientRect());
                }
            });
        }
    });

    function showToolBySelection() {
        clearClass();
        const selection = window.getSelection();
        if (selection.type === "Range" && selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            showTool(range.getBoundingClientRect());
            return true;
        }
        return false;
    }

    function getTextMarkedUniqClass(ele) {
        for (const kls of ele.classList) {
            if (kls.startsWith("x-plugin-time-")) {
                return kls;
            }
        }
        return null;
    }

    $("#x-plugin-textSelect").on("click", (evt) => {
        if (selectType(evt.target, "text")) {
            showToolBySelection();

            article.on("mouseup", (e) => {
                if (!showToolBySelection()) {
                    if ($(e.target).hasClass("x-plugin-text-marked")) {
                        $(e.target).addClass("x-plugin-text-clicked");
                        showTool(e.target.getBoundingClientRect());
                    }
                }
            });
        }
    });

    $(".x-plugin-tool-btn").on("click", (evt) => {
        const type = $(evt.target).data("type");

        if ("text" === mediaType) {
            const current = $(".x-plugin-text-clicked");
            const selection = window.getSelection();
            if (selection.type === "Range" && selection.rangeCount > 0) {
                const range = new Range(window.document);

                const sel = window.getSelection();
                if (sel && sel.rangeCount) {
                    const firstRange = sel.getRangeAt(0);
                    const lastRange = sel.getRangeAt(sel.rangeCount - 1);
                    range.setStart(firstRange.startContainer, firstRange.startOffset);
                    range.setEnd(lastRange.endContainer, lastRange.endOffset);
                }

                range.applyInlineStyle('i', {
                    "class": "x-plugin-text-marked x-plugin-time-" + new Date().getTime(),
                    "data-mark-type": type
                });
                range.select();
            } else if (current.length) {
                const kls = getTextMarkedUniqClass(current.get(0));
                if (kls) {
                    if (type === current.attr("data-mark-type")) {
                        $('.' + kls).contents().unwrap();
                    } else {
                        $('.' + kls).attr({
                            "data-mark-type": type,
                            "data-media-type": mediaType
                        });
                    }
                }
            }
            clearClass();
        } else {
            const current = $(".x-plugin-clicked");
            if (current.hasClass("x-plugin-marked")) {
                if (type === current.attr("data-mark-type")) {
                    current.removeClass("x-plugin-marked");
                    current.removeAttr("data-mark-type");
                    current.removeAttr("data-media-type");
                } else {
                    current.attr({
                        "data-mark-type": type,
                        "data-media-type": mediaType
                    });
                }
            } else {
                current.addClass("x-plugin-marked");
                current.attr({
                    "data-mark-type": type,
                    "data-media-type": mediaType
                });
            }
        }
    });

    $("#x-plugin-downloadBtn").on("click", async (evt) => {
        clearClass();
        const btn = $(evt.target);
        const oldName = btn.text();
        btn.text("正在处理中");

        const zip = new JSZip();

        const image_list = [];
        for (const ele of $("figure img", article)) {
            const imageUrl = $(ele).attr("src");
            const index = $(ele).attr("index");
            const filePath = `assets/${paperId}/` + (index ? `image_${index}.jpg` : imageUrl.split("/").pop());

            image_list.push({
                index: index,
                url: imageUrl,
                target: filePath
            });
            $(ele).attr("local-src", imageUrl);

            // const response = await fetch(imageUrl, {
            //     cache: 'force-cache' // 强制使用缓存
            // });
            // zip.file(filePath, response.blob(), {binary: true, createFolders: true});

            // $(ele).attr("local-src", filePath);
        }

        const paperInfo = {
            ref: result[tabId]?.url,
            doi: paperId,
            title: paperTitle,
            image_list: image_list
        };

        for (const ele of $(".tables .groups[caption]", article)) {
            const index = $(ele).attr("index");
            const filePath = `table_${index}.txt`;

            $("tbody, thead, table, td, th, tr", ele).removeAttr("class");
            zip.file(filePath, $(ele).html(), {createFolders: true});
            $(ele).attr("local-src", filePath);
        }

        // for (const ele of $(".Appendices a", article)) {
        //     const docUrl = $(ele).attr("href");
        //     const filePath = docUrl.split("/").pop();
        //
        //     const response = await fetch(docUrl);
        //     zip.file(filePath, response.blob(), {binary: true, createFolders: true});
        //     $(ele).attr("href", filePath);
        // }

        const markList = article.find("[data-mark-type]");
        const textSet = new Set();
        for (const ele of markList) {
            if (!paperInfo[$(ele).data("mark-type")]) {
                paperInfo[$(ele).data("mark-type")] = [];
            }

            if ($(ele).hasClass("x-plugin-text-marked")) {
                const kls = getTextMarkedUniqClass(ele);
                if (!textSet.has(kls)) {
                    paperInfo[$(ele).data("mark-type")].push({
                        selector: `.${kls}`,
                        mediaType: "text",
                        content: $(`.${kls}`).get().map(item => $(item).text().trim()).join(" ")
                    });
                    textSet.add(kls);
                }
            } else if ($(ele).hasClass("x-plugin-marked")) {
                const mediaType = $(ele).data("media-type");
                const captions = $(".captions", ele).clone();
                $("span.label", captions).remove();
                const obj = {
                    selector: selectorGenerator.getSelector(ele),
                    mediaType: mediaType,
                    title: captions.text().replace(/^\./, '').replace(/\.$/, '').trim()
                };
                switch (mediaType) {
                    case "table":
                        obj["content"] = $("<div/>").append($("table", ele).clone()).html()
                        break;
                    case "image":
                        obj["content"] = $("img", ele).attr("local-src")
                        break;
                }
                paperInfo[$(ele).data("mark-type")].push(obj);
            }
        }

        // const response = await fetch(chrome.runtime.getURL("css/options.css"));
        // zip.file("assets/options.css", response.blob(), {binary: true, createFolders: true});

        // const html = $("<html/>");
        // html.append(
        //     $("<head/>")
        //         .append($("<title/>").text(paperTitle))
        //         .append(cssLink.clone())
        //         .append($("<link/>").attr({
        //             rel: "stylesheet",
        //             type: "text/css",
        //             href: "assets/options.css",
        //         }))
        // );
        // html.append($("<body/>").append(article.clone()));

        $("#body>div:first>section, #body>div:first>div").each((i, ele) => {
            const para = htmlToTextWithNewlines($(ele)[0]);
            zip.file(`section_${i}.txt`, para, {createFolders: true});
        });

        // zip.file(`${paperId}.html`, `<html lang="en">${html.html()}</html>`);
        zip.file(`${paperId}.json`, JSON.stringify(paperInfo, null, 4));
        zip.generateAsync({type: "blob"}).then(output => {
            btn.text(oldName);

            const url = URL.createObjectURL(output);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${paperId}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        });
    });
});
