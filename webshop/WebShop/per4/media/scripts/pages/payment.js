require([], function () {
    var View = Backbone.View.extend({
            el:$("#payment-page")
            , events : {"click input[name=payment_method]":"switchPaymentMethod"}
            , initialize: function () {
            }
            , switchPaymentMethod : function(e){
                    var $target = $(e.target);
                    this.$el.find(".paymentforms").addClass("hidden");
                    this.$el.find(".for-"+this.options.methodTranslation[$target.val()]).removeClass("hidden");
                }
        })
        , page = new View(window.__options__);
    return page;
});
