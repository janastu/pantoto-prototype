
function add_hidden_field(name,value){
    $('#id_extra_fields').append("<input type='hidden' name='"+name+"' value='"+value+"' />");
    document.frmaddedit.submit();
}
