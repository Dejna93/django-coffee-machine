$( document ).ready(function() {
    $("#coffee_maker").click(function(){
      var button = $(this);
      $.post( "", {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            method: "make_coffee",
            coffee_type: $("#id_coffee_type").val(),
        }, function( data ) {
        if (data["problems"]){
            $("#problems").html(data["problems"]);
            button.attr("disabled", true);
            $("[id*='options']").each(function(){
                $(this).attr("disabled", false);
            });
        }
        if (data["image"]){
            $("#coffee_image").html("<img src='"+data["image"]+"'>");
        }
        });
    });

    var change_options = function(option){
        $.post( "/ajax/", {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            method: option,
        }, function( data ) {
             $("#problems").html("");
             $("#coffee_maker").attr("disabled", false);
             $("[id*='options']").each(function(){
                $(this).attr("disabled", true);
             })
        });
    };

    $("[id*='options']").click(function(){
        change_options($(this).attr("id"));
    });


});
