require([], function () {
    var View = Backbone.View.extend({
        el: $("#ArticleDetail")
        , articleTable : $("#tbArticles")
        , events : {"click .addToCartBtn": "addToCart"
                , "keyup .cartQtyInput": "onKeyUp"
                    , "click .listed-option-link": "filterByOption"}
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

        , findAllArticleRows: function(ref){
            return this.articleTable.find("tr.articleoption_row[article="+ref+"]");
        }

        , reCalculateOptions: function($row, hasDiscount){
            var $first_row = $row.first()
                    , pricing = parseFloat($first_row.find(".base_price").html())
                    , isDiscounted = false;

            if(hasDiscount){
                var discountQty = parseFloat($first_row.find(".discountQty").html())
                    , discountPrice = parseFloat($first_row.find(".discountPrice").html())
                    , totalQty = 0;

                $row.find(".cart_qty").each(
                    function(){
                        var t = parseInt($(this).text(), 10); if(!isNaN(t)){totalQty += t;}
                    }).end().find(".cartQtyInput").each(
                    function(){
                        var t = parseInt($(this).val(), 10); if(!isNaN(t)){totalQty += t;}
                    });
                if(totalQty >= discountQty){
                    pricing = discountPrice;
                    isDiscounted = true;
                }

            }

            $row.each(function(idx, elem){
                var $elem = $(elem)
                        , resultHolder = $elem.find(".articleoption_total")
                        , qty = parseInt($elem.find(".cartQtyInput").val(), 10)
                        , newTotal = qty*pricing;
                if(isNaN(newTotal)){
                    resultHolder.html(0);
                } else {
                    resultHolder.html(newTotal.toFixed(2));
                }
            });
            this.calculateTotal();
        }
        , onKeyUp: function(e){
            if(e.keyCode == 13){
                this.addToCart();
            } else {
                var $target = $(e.target)
                    , $row = $target.closest(".articleoption_row")
                    , hasDiscount = $row.find(".discount").length > 0;
                if(hasDiscount){
                    this.reCalculateOptions(this.findAllArticleRows($row.attr("article")), true);
                } else {
                    this.reCalculateOptions($row, false);
                }


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

        , filterByOption: function(e){
            var $target = $(e.target).closest(".listed-option-link")
                    , ref = $target.attr("title");
            if($target.hasClass("selected")){
                $(".articleoption_row.option-" + ref).removeClass("selected");
                $(".articleoption_row:not(.selected)").addClass("hidden");
                $target.removeClass("selected");
            } else {
                $(".articleoption_row.option-" + ref).addClass("selected").removeClass("hidden");
                $(".articleoption_row:not(.selected)").addClass("hidden");
                $target.addClass("selected");
            }
            if($(".articleoption_row.selected").length == 0){
                $(".articleoption_row").removeClass("hidden");
            }
        }
    })
    , page = new View(window.__options__);
    return page;
});