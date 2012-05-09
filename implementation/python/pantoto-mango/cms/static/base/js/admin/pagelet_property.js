$(document).ready(function(){

    $('#id_row_attach_views').hide();

    $('#id_on_submit').change(submit_changed);

    $('#id_auto_title').change(auto_title_changed);

    $('#id_submit_once').change(submit_once_changed);

    submit_changed();

    auto_title_changed();

    submit_once_changed();
    
});

function auto_title_changed(){
    if($('#id_auto_title').attr('checked')){
        $('#id_row_title_template').show();
    }
    else{
        $('#id_row_title_template').hide();
    }
}

function submit_once_changed(){
    if($('#id_submit_once').attr('checked')){
        $('#id_row_submit_once_personas').show();
        $('#id_row_submit_once_message').show();
    }
    else{
        $('#id_row_submit_once_personas').hide();
        $('#id_row_submit_once_message').hide();
    }
}



function submit_changed(){

    var val = $("#id_on_submit").val();
    if( val == "attach_views"){
        $('#id_row_attach_views').show();
    }
    else{
        $('#id_row_attach_views').hide();
    }

}

