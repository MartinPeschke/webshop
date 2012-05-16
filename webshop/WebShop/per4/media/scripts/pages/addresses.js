require([], function () {
    var View = Backbone.View.extend({
        el: $("#address-form")
        , events : {"click #id_same_address":"switchSameAddress"}
        , initialize: function () {
            this.same_address_box = this.$el.find("#id_same_address");
            this.switchSameAddress();
        }
        , switchSameAddress: function(){
            var isSame = !!this.same_address_box.attr('checked')
                , $el = this.$el;
            if(isSame){
                $el.find(".shipping-detail").attr("readonly", true).each(function(idx, elem){
                    var $elem = $(elem);
                    $elem.data({'data-value':$elem.val()});
                    $elem.val($el.find(".billing-detail[_form_key="+ $elem.attr("_form_key") +"]").val());
                });
                $el.find(".billing-detail").on({"keyup.sameaddress change.sameaddress click.sameaddress":function(e){
                    var $target = $(e.target);
                    $el.find(".shipping-detail[_form_key="+ $target.attr("_form_key") +"]").val($target.val());
                }});

            } else {
                $el.find(".shipping-detail").removeAttr("readonly").each(function(idx, elem){
                    var $elem = $(elem);
                    $elem.val($elem.data('data-value')||$elem.val());
                });
                $el.find(".billing-detail").unbind(".sameaddress");
            }
        }
    })
    , page = new View(window.__options__);
    return page;
});