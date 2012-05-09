$(document).ready(function(){
    $('#id_type').change(type_selected);
    type_selected();
});

function type_selected(){
    val = $('#id_type').val();
    if(val == "TextField"){
        $('#id_row_rows').show();
        $('#id_row_cols').show();
        $('#id_row_max_length').hide();
        $('#id_row_choices').hide();
    }
    else if(val == "ReferenceField" || val == "ListField" || val == "CheckboxField" || val == "RadioField"){
        $('#id_row_choices').show();
        $('#id_row_max_length').hide();
        $('#id_row_rows').hide();
        $('#id_row_cols').hide();
    }
    else{
        $('#id_row_rows').hide();
        $('#id_row_cols').hide();
        $('#id_row_choices').hide();
        $('#id_row_max_length').show();
    }
}

