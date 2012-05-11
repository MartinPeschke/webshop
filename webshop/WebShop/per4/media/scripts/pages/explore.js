require([], function () {
    var View = Backbone.View.extend({
        el: $("#ArticleDetail")
        , events : {"click .addToCartBtn": "addToCart"
                , "keyup .cartQtyInput": "reCalculatePrice"}
        , initialize: function () {
            this.originalTotalBox = this.$el.find("#totalPrice");
            this.originalTotal = this.originalTotalBox.html();
            this.calculateTotal();
        }

        , addToCart : function(e){
            var view = this
                    , items = this.$el.find('.cartQtyInput[value!=""]').serialize();
            $.ajax({
                data : items,
                url: this.options.addToCartUrl,
                type: 'POST', dataType: 'json',
                success : function(data, textStatus) {
                    $('#shopping-cart-container').html(data['cart_html']);
                    view.$el.find('.cartQtyInput[value!=""]').each(function(idx, elem){
                        var $elem = $(elem)
                            , $target = $elem.parent().find(".cart_qty")
                            , row = $target.closest(".articleoption_row")
                            , newAddedQty = parseInt($target.text(), 10) + parseInt(elem.value, 10);
                        if(newAddedQty){
                            $target.html(newAddedQty)
                                    .closest(".cart-quantity-wrapper ").removeClass("hidden");
                        } else {
                            $target.html(0)
                                    .closest(".cart-quantity-wrapper ").addClass("hidden");
                        }

                        elem.value = "";
                        row.find('.articleoption_total').html(0);
                    });
                    view.calculateTotal();
                },
                error : function(data, textStatus) {
                    document.write(data.responseText);
                    document.close();
                }});
        }
        , reCalculatePrice: function(e){
            if(e.keyCode == 13){
                this.addToCart();
            } else {
                var $target = $(e.target)
                    , row = $target.closest(".articleoption_row")
                    , qty = parseInt($target.val(), 10)
                    , pricing = parseFloat(row.find(".base_price").html())
                    , hasDiscount = row.find(".discount").length > 0
                    , resultHolder = row.find(".articleoption_total")
                    , newTotal = pricing * qty;
                    if($target.val().length == 0){
                        resultHolder.html(0);
                        $target.removeClass("error");
                    } else if(isNaN(newTotal)){
                        resultHolder.html(0);
                        $target.addClass("error");
                    } else {
                        resultHolder.html(newTotal.toFixed(2));
                        $target.removeClass("error");
                    }
                    this.calculateTotal();
            }
        }
        , calculateTotal : function(){
            var total = 0;
            this.$el.find(".articleoption_total").each(function(idx, elem){
                  total += parseFloat(elem.innerText, 10);
            });
            if(isNaN(total)){
                this.originalTotalBox.html(this.originalTotal);
            } else {
                this.originalTotalBox.html(total.toFixed(2));
            }
        }
    })
    , page = new View(window.__options__);
    return page;
});