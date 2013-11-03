$(function(){
    $(function () {
        if (typeof jQuery.validator != 'undefined') {
            jQuery.validator.addMethod("phone-number", function (value, element) {
                return this.optional(element) || /^[+]?([0-9]+[()/-]?)+$/gi.test(value.replace(/ /g, ""));
            }, "Bitte geben sie eine Telefonnummer an.");
        }
    });


    $('#language_bar span[lang]').on({"click":function(evt){
        $('#languageCode').val($(evt.target).parents('span.flag').attr('lang'));
        $('#setlang').submit();
    }});

    (function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s); js.id = id;
        js.src = "//connect.facebook.net/en_GB/all.js#xfbml=1&appId=" + window.__options__.FB_APP_ID;
        fjs.parentNode.insertBefore(js, fjs);
    } (document, 'script', 'facebook-jssdk'));

    $(function () {
        var container = $('#fbLikeContainer');
        $(window).bind("load resize", function () {
            var container_width = container.width();
            container.html('<div class="fb-like-box" ' +
                    'data-href="http://www.facebook.com/Per4Store"' +
                    ' data-width="' + container_width + '" data-height="430" data-show-faces="true" ' +
                    'data-stream="false" data-header="true"></div>');
            FB.XFBML.parse(container[0]);
        });
    });

    switchLinePane = function(page){
        $.ajax({
            data : {page:page, promo: '1'},
            url: '/'+shop_ref+'/'+line_ref+'/page/',
            type: 'POST', dataType: 'json',
            success : function(data, textStatus) {
                $('#center_block_thumbnails').html(data['html']);
                $('#center_block_paginating').children('a').removeClass('selected');
                $($('#center_block_paginating').children('a').get(data['page_no']-1)).addClass('selected');

            },
            error : function(data, textStatus) {
                document.write(data.responseText);
                document.close();
            }});
    }
});