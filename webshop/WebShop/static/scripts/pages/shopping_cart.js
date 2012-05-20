require([], function () {
    var View = Backbone.View.extend({
            el:$("#shopping-cart-body")
            , events : {"click .refresh-cart-btn": "refreshCart"
                    , "keyup .cartQtyInput": "refreshCartFromKeyEvent"
                    , "click .submit-cart-btn": "submitCart"
                    , "click .delete-link": "deleteItem"}
            , initialize: function () {
                    this.$el.find(".delete-link").each(function(idx, elem){
                       var $elem = $(elem);
                        $elem.attr("_href", $elem.attr("href"));
                        $elem.removeAttr("href");
                    });
            }

            , refreshCartFromKeyEvent: function(e){
                    if(e.keyCode == 13){
                        this.refreshCart(e);
                    }
                }
            , refreshCart: function(e){
                var items = this.$el.find('.cartQtyInput[value!=""]').serialize();
                $.ajax({
                    data : items,
                    url: this.options.updateCartUrl,
                    type: 'POST',
                    success : function(data, textStatus) {
                        window.location.reload();
                    },
                    error : function(data, textStatus) {
                        document.write(data.responseText);
                        document.close();
                    }});
            }
            , submitCart: function(e){

            }
            , deleteItem: function(e){
                window.location.href = $(e.target).closest(".delete-link").attr("_href");
            }
        })
        , page = new View(window.__options__);
    return page;
});
