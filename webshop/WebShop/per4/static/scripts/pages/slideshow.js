require([], function () {
    var options = window.__options__.slideShow
    , View = Backbone.View.extend({
        el: $(options.root)
        , entryTempl : _.template('<div><a href="<%=link%>"><img src="<%=src%>" alt="<%=title%>" /><p><%=description%></p></a></div>')
        , events : {}
        , initialize: function () {
            var view = this;
            $.ajax({
                        url: this.options.getURL
                        , success : function(resp, status, xhr){
                            var elems = [];
                                _.each(resp, function(elem){
                                    elems.push(view.entryTempl(elem));
                                });
                            view.$el.html(elems.join(""));

                            view.$el.anythingSlider();

                        }
                        , type:"GET"
                    });
        }
    })
    , page = new View(options);
    return page;
});