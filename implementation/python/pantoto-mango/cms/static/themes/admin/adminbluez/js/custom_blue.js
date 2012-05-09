/*
	Global values
*/

var chartWidth = '650px';
var chartHeight = '240px';


/*
	Find element's Y axis position
*/

function findPosY(obj) 
{
	var curtop = 0;
	if (obj.offsetParent) 
	{
		while (1) 
		{
			curtop+=obj.offsetTop;
			if (!obj.offsetParent) 
			{
				break;
			}
			obj=obj.offsetParent;
		}
	} 
	else if (obj.y) 
	{
		curtop+=obj.y;
	}
		
	return curtop;
}

/*
	Find element's X axis position
*/

function findPosX(obj) 
{
	var curtop = 0;
	if (obj.offsetParent) 
	{
		while (1) 
		{
			curtop+=obj.offsetLeft;
			if (!obj.offsetParent) 
			{
				break;
			}
			obj=obj.offsetParent;
		}
	} 
	else if (obj.x) 
	{
		curtop+=obj.x;
	} 
	
	return curtop;
}

/*
	Setup chart from given table and type
*/

function setChart(tableId, type, wrapper)
{
	//clear existing chart before create new one
	$(wrapper).html('');

	$(tableId).visualize({
		type: type,
		width: chartWidth,
		height: chartHeight,
		colors: ['#7EC421', '#9FBAD4']
	}).appendTo(wrapper);
	
	//if IE then need to add refresh event
	if (navigator.appName == "Microsoft Internet Explorer")
	{
		$('.visualize').trigger('visualizeRefresh');
	}
}

/*
	Setup notification badges for shortcut
*/
function setNotifications()
{
	// Setup notification badges for shortcut
	$('#shortcut_notifications span').each(function() {
		if($(this).attr('rel') != '')
		{
			target = $(this).attr('rel');
			
			if($('#' +target).length > 0)
			{
				var Ypos = findPosY(document.getElementById(target));
				var Xpos = findPosX(document.getElementById(target));
				
				$(this).css('top', Ypos-24 +'px');
				$(this).css('left', Xpos+60 +'px');
			}
		}
	});
	$('#shortcut_notifications').css('display', 'block');
}

$(function(){ 
	
	// Preload images
	$.preloadCssImages();



    // Find all the input elements with title attributes and add hint to it
    $('input[title!=""]').hint();
    
    
    
    // Setup WYSIWYG editor
    $('#wysiwyg').wysiwyg({
    	css : "css/wysiwyg.css"
    });
    
    
    
    // Setup slider menu (left panel)
    $('#main_menu').accordion({
			collapsible: true,
			autoHeight: false
	});
	
	
	// Setup show and hide left panel
	$('#hide_menu').click(function(){
		$('#left_menu').hide();
		$('#show_menu').show();
		$('body').addClass('nobg');
		$('#content').css('marginLeft', 30);
		$('#wysiwyg').css('width', '97%');
		setNotifications();
	});
	
	$('#show_menu').click(function(){
		$('#left_menu').show();
		$(this).hide();
		$('body').removeClass('nobg');
		$('#content').css('marginLeft', 240);
		$('#wysiwyg').css('width', '97%');
		setNotifications();
	});
	
	
	// Setup click to hide to all alert boxes
	$('.alert_warning').click(function(){
		$(this).fadeOut('fast');
	});
	
	$('.alert_info').click(function(){
		$(this).fadeOut('fast');
	});
	
	$('.alert_success').click(function(){
		$(this).fadeOut('fast');
	});
	
	$('.alert_error').click(function(){
		$(this).fadeOut('fast');
	});
	
	
	
	
	
	
	// Setup left panel calendar
	$("#calendar").datepicker({
		nextText: '&raquo;',
		prevText: '&laquo;'
	});
	
	// Setup datepicker input
	$("#datepicker").datepicker({
		nextText: '&raquo;',
		prevText: '&laquo;',
		showAnim: 'slideDown'
	});
	
	
	
	// Setup minimize and maximize window
	$('.onecolumn .header span').click(function(){
		if($(this).parent().parent().children('.content').css('display') == 'block')
		{
			$(this).css('cursor', 's-resize');
		}
		else
		{
			$(this).css('cursor', 'n-resize');
		}
		
		$(this).parent().parent().children('.content').slideToggle('fast');
	});
	
	$('.twocolumn .header span').click(function(){
		if($(this).parent().parent().children('.content').css('display') == 'block')
		{
			$(this).css('cursor', 's-resize');
		}
		else
		{
			$(this).css('cursor', 'n-resize');
		}
		
		$(this).parent().parent().children('.content').slideToggle('fast');
	});
	
	$('.threecolumn .header span').click(function(){
		if($(this).parent().parent().children('.content').css('display') == 'block')
		{
			$(this).css('cursor', 's-resize');
		}
		else
		{
			$(this).css('cursor', 'n-resize');
		}
		
		$(this).parent().children('.content').slideToggle('fast');
	});
	
	
	
	// Check or uncheck all checkboxes
	$('#check_all').click(function(){
		if($(this).is(':checked'))
		{
			$('form#form_data input:checkbox').attr('checked', true);
		}
		else
		{
			$('form#form_data input:checkbox').attr('checked', false);
		}
	});
	
	
	
	// Setup notification badges for shortcut
	setNotifications();
	
	
	
	// Setup modal window link
	$('#shortcut li a').fancybox({
		padding: 0, 
		titleShow: false, 
		overlayColor: '#333333', 
		overlayOpacity: .5
	});
	
	// Add tooltip to shortcut
	$('#shortcut li a').tipsy({gravity: 's'});
	
	$('#btn_modal').fancybox({
		padding: 0, 
		titleShow: false, 
		overlayColor: '#333333', 
		overlayOpacity: .5,
		href: 'modal_window.html'
	});
	
	
	
	// Add tooltip to edit and delete button
	$('.help').tipsy({gravity: 's'});
	
	
	
});

$(document).ready(function() {
	
	//Add ability to click link if href is not empty
	$('#main_menu').find('li a').click(function(){
		if($(this).attr('href').length > 0)
		{
			location.href = $(this).attr('href');
		}
	});
});