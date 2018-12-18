$( document ).ready(function() {
    var send_request = function(){
    $.ajax({url: "", success: function(result){
        console.log(result);
    }});
    };

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
        $("#cup").html(data["html"]);
        });
    });

    var change_options = function(option){
        $.post( "/ajax/", {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            method: option,
        }, function( data ) {
            $("#problems").html("");
             $("#coffee_maker").attr("disabled", false);
             $(option).attr("disabled", true);
        });
    };

    $("[id*='options']").click(function(){
        change_options($(this).attr("id"));
    });


});
