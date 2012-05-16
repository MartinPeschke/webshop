require([], function () {
    var View = Backbone.View.extend({
            el:$("#payment-page")
            , events : {"click input[name=payment_method]":"switchPaymentMethodOnClick"}
            , initialize: function () {
                this.switchPaymentMethod(this.$el.find("input.paymentmethod:checked"));
            }
            , switchPaymentMethodOnClick : function(e){
                this.switchPaymentMethod($(e.target));
            }
            , switchPaymentMethod : function($target){
                this.$el.find(".paymentforms").addClass("hidden");
                this.$el.find(".for-"+this.options.methodTranslation[$target.val()]).removeClass("hidden");
            }
        })
        , page = new View(window.__options__);
    return page;
});
