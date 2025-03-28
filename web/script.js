$(document).ready(function () {
    eel.expose(add_image);
    function add_image(imgObj) {
        const { mime, data } = imgObj;

        // Validate MIME type
        if (!mime || !data || !mime.startsWith("image/")) {
            console.error("Invalid image data");
            return;
        }

        // Build proper data URL
        const dataUrl = `data:${mime};base64,${data}`;

        // Create <img> element
        const $imgElement = $("<img>")
            .attr("src", dataUrl);

        // Create wrapper with class .image
        const $wrapper = $("<div class='image'>")
            .css("position", "relative") // Needed for absolute medal positioning
            .append($imgElement);

        // Append to container
        const $container = $(".images");
        if ($container.length > 0) {
            $container.append($wrapper);
            setTimeout(function () {
                $wrapper.addClass("show");
            }, 100);
        } else {
            console.warn("No container found for selector .images");
        }
    }

    eel.expose(send_message);
    function send_message(text) {
        let delay = 50;
        const $target = $(".message");
        $target.empty();

        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                $target.append(text[i]);
                i++;
            } else {
                clearInterval(interval);
            }
        }, delay);
    }

    eel.expose(rank);
    function rank(values) {
        const medals = ["🥉", "🥈", "🥇"];
        const delayPerMedal = 800;

        const $wrappers = $(".images .image");

        if (values.length !== $wrappers.length) {
            console.error("Mismatch between values and image count");
            return;
        }

        // Create array of index-value pairs and sort
        const ranked = values
            .map((val, index) => ({ val, index }))
            .sort((a, b) => a.val - b.val); // Ascending: bronze first

        ranked.forEach((item, rankIndex) => {
            setTimeout(() => {
                const $wrapper = $wrappers.eq(item.index);

                // Create and add medal
                const $medal = $("<div class='medal'>")
                    .text(medals[rankIndex]);
                   

                $wrapper.append($medal);
                $medal.addClass("show");

                 // Add winner/loser classes after all medals are placed
            if (rankIndex === 2) {
                $wrapper.addClass("winner"); 
            } else {
                $wrapper.addClass("loser"); 
            }
            }, rankIndex * delayPerMedal);
        });
    }

    eel.expose(end_round);
    function end_round(values) {
        $(".message").text("");
        $(".loser .medal").removeClass("show");
        setTimeout(function () {
            $(".loser").addClass("disapear")
            setTimeout(function () {
                //destroy
                $(".loser").remove();
            }, 1000);
        }, 200);
        
    }

    eel.expose(remove_all_medals);
    function remove_all_medals(values) {
        $(".medal").remove();
    }
});
