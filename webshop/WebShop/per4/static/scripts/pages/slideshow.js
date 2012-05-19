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
                                slider = view.$el.find("#slideShow");
                                _.each(resp, function(elem){
                                    elems.push(view.entryTempl(elem));
                                });
                            slider.html(elems.join(""));

                            slider.anythingSlider({ expand : true, buildStartStop : false, buildArrows : false, autoPlay : true, animationTime       : 300});


                        }
                        , type:"GET"
                    });
        }
    })
    , page = new View(options);
    return page;
});