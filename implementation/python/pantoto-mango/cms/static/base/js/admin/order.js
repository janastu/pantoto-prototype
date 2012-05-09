var sort;
var order = new Array();

function sort_update(){
    order = new Array();
    $('#sort-list').find('li').each(function(i,ele){
        order.push($(ele).attr('id'));
    });
}

function order_updated(data){
    data = eval("("+data+")");
    window.location = data['redirect'];
}

function send_order(){
    $.ajax({url:location.pathname,type:'post',data:{'order':JSON.stringify(order)},success:order_updated});
}

$(document).ready(function() {
   sort = $("#sort-list").sortable({
      handle : '.handle',
      update : sort_update
   });
   sort_update();
});

