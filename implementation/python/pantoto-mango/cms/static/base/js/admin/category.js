
$(document).ready(function(){
    $('#id_type').change(type_selected);
    type_selected();
    $('#list_table').addClass('treeTable');
    $('.treeTable').treeTable({
        initial: "collapsed"
    });
});

function type_selected(){
    val = $('#id_type').val();
    if( val == "link"){
        $('#id_row_link').show();
    }
    else {
        $('#id_row_link').hide();
    }
}

