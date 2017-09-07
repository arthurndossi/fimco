function ForexTicker(update_interval) {
    this.update_interval = update_interval || 500;
    this.start();
}

ForexTicker.prototype.start = function () {
    ForexTicker.updateQuotes();
    this.interval = setInterval(function () {
        ForexTicker.updateQuotes();
    }, this.update_interval);
};

ForexTicker.prototype.stop = function () {
    clearInterval(this.interval);
};

ForexTicker.allCurrencyPairsOnPage = function () {
    var pairs = [];

    $('[data-currency-pair]').each(function () {
        pairs.push($(this).attr('data-currency-pair'));
    });

    return pairs;
};

ForexTicker.updateQuotes = function () {
    $.ajax({
        url: "https://forex.1forge.com/1.0.1/quotes?referer=" + window.location.hostname + "&pairs=" + ForexTicker.allCurrencyPairsOnPage().join(','),
    }).done(function (response) {
        for (var i = 0; i < response.length; i++) {
            var item = response[i];

            var jquery_object = $('[data-currency-pair=' + item.symbol + ']').first();

            var price = parseFloat(jquery_object.attr('data-price'));
            var new_price = item.price.toFixed(5);
            jquery_object.attr('data-price', new_price);

            jquery_object.find(".top").text(new_price.substring(0, 4));
            jquery_object.find(".bottom .first").text(new_price.substring(4, 6));
            jquery_object.find(".bottom .last").text(new_price.substring(6, 7));

            var direction = '';

            if (new_price - price > 0) {
                direction = 'up';
            }
            else if (new_price - price < 0) {
                direction = 'down';
            }

            jquery_object.removeClass('up down even').addClass(direction);
        }
    });
};