$(function(){
    $('#language_bar span[lang]').click(setLanguage);

    (function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s); js.id = id;
        js.src = "//connect.facebook.net/en_GB/all.js#xfbml=1&appId={{ FB_APP_ID }}";
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
});