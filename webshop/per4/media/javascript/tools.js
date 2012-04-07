/**
 * Business Logics
 */
 
verifyEnterToSubmit = function(id, func){
	if(func)
		$(id).keyup(func);
	else
		$(id).keyup(verifyEnter);		
}

verifyEnter = function(evt){
	if(evt.keyCode==13){
		var a = $(evt.target).parents("form").get(0).submit()
	} 
}
 
function login() {
	$('login_error').hide();	
	
	$.ajax({
		data : $('#login_form').serialize(),
		url : '/user/rlogin/', 
		type: 'POST', dataType: 'json',
		success : 
			function(data, textStatus) {
				if(data['result']){
					if($('#forwardURL'))
						window.location.href=$('#forwardURL').val();
				} else {
					$('#login_error').html(data['error']).show();
				}
		},
		error : function(data, textStatus) {
			document.write(data.responseText);
			document.close();
		}});
}

function setLanguage(evt, next) {
	$('#languageCode').val($(evt.target).parents('span.flag').attr('lang'));
	if (next) $('#next').val(next);
	$('#setlang').submit();
}

/* ------------------- Articles ------------------------ */

jQuery.fn.fadeToggle = function(speed, easing, callback) {
   return this.animate({opacity: 'toggle'}, speed, easing, callback);
}; 

function expandOption(event) {
	var appear = false;
	$('#tbArticles .optionLink[title='+this.title+']').each(function(){
		var row = $(this).parents('tr').get(0);
		if($(row).hasClass('notfirst')){$(row).fadeToggle();}
	});
	$(this).toggleClass('olselected').toggleClass('oldeselected');
}

/* ist ein wenig langsam, vergisst manchmal zu berechnen, wieso */
function calcPrice() {
	calculateRow(0, this);
	updateTotalPrice();
}
/*  discount preis nicht ueber optionen  */

function calculateRow(index, ctrl) {
	var qty = ctrl.value;
	$(ctrl).prev('span').children('span.cart_qty').show();
	if (!/^[0-9]*$/.test(qty)) {
		alert(INTEGER_WARNING);
		ctrl.value = '0';
		return;
	} else
		qty = parseInt(qty);
	
	var price = parseFloat($('span', $(ctrl).parent().prevAll('td.pricing')).get(0).innerHTML);
	var discountCell = $(ctrl).parent().prevAll('td.discount').children('div');
	var discountQty = null;

	if(discountCell && discountCell.length)
		discountQty = parseInt(discountCell.children('span').get(0).innerHTML);

	if(discountQty && qty >= discountQty)
		price = parseFloat(discountCell.next().get(0).innerHTML);
	if(isNaN(qty))qty = 0;

	$(ctrl).parent().nextAll('td.total').children('span').text(parseFloat((price * qty * 100)/100).toFixed(2));
}

function updateTotalPrice() {
	lastCol = $('#tbArticles').children('tbody').children('tr').children('td.total').children('span');
	var totalPrice = 0.00;
	for (var i = 0, j = lastCol.length; i < j; i++) {
		totalPrice += parseFloat(lastCol[i].innerHTML);
	}
	$('#totalPrice').text(parseFloat((totalPrice * 100)/100).toFixed(2));
}

showAllColors = function(evt) {
	if (/down.gif$/.test(evt.target.src)) {
		$($(evt.target).parents('tbody').get(0)).children('tr.notfirst').fadeIn();
		evt.target.src = '/media/images/up.gif';
	} else {
		$($(evt.target).parents('tbody').get(0)).children('tr.notfirst').fadeOut();
		evt.target.src = '/media/images/down.gif';
	}
}

function addToCart() {
	var items = $('#tbArticles input.ultramini[value!=0]').serialize();

	$.ajax({
		data : items, 
		url: '/user/add_to_cart/',
		type: 'POST', dataType: 'json',
		success : function(data, textStatus) {
			$('#rightBox').html(data['cart_html']);
			$(data['added_id_qty']).each(function(i)
					{ 
						var elem = $('#'+this[0]).children('td.data').children('span');
						elem.children('span.cart_qty').text(this[1]);
						elem.show();
					});
			
			$('#tbArticles input.ultramini[value!=0]').val('0');
			$('#tbArticles input').each(calculateRow);
			updateTotalPrice();
			
		},
		error : function(data, textStatus) {
			document.write(data.responseText);
			document.close();
		}});
}

/* -------------------- Line Pane Switching --------------- */

switchLinePane = function(page){
	$.ajax({
		data : {page:page, promo: '1'}, 
		url: '/'+shop_ref+'/'+line_ref+'/page/',
		type: 'POST', dataType: 'json',
		success : function(data, textStatus) {
			$('#center_block_thumbnails').html(data['html']);
			$('#center_block_paginating').children('a').removeClass('selected');
			$($('#center_block_paginating').children('a').get(data['page_no']-1)).addClass('selected');
			
		},
		error : function(data, textStatus) {
			document.write(data.responseText);
			document.close();
		}});
}

function previousPage(current_page, count) {
	renderView('center_block_paginating', 'page_flip_template', {page_num:current_page-1, page_count:count});
}

function nextPage(current_page, count) {
	renderView('center_block_paginating', 'page_flip_template', {page_num:current_page+1, page_count:count});
}

	
/**
* Validators
*/
function checkMail(eml) {
	if (/^[.\w]([(\/)(\-)(\+).\w])*@([(\-)\w]{1,64}\.){1,7}[(\-)\w]{1,64}$/.test(eml)) 
	{
		$.ajax({
			data : {email: eml}, 
			url: '/user/checkmail/',
			type: 'POST', dataType: 'json',
			success : function(data, textStatus) {
				if (data['result']) {
				        $('#error_email').html('<label class="reg_ico"><img align="absmiddle" src="/media/images/accept.png" /></label>');
				} else {
				        $('#error_email').html('<label class="reg_ico"><img align="absmiddle" src="/media/images/cross.png" />Your email address has been registered.</label>');
				}			
			},
			error : function(data, textStatus) {
				document.write(data.responseText);
				document.close();
			}});		
	} else {
	    $('#error_email').html('<label class="reg_ico"><img align="absmiddle" src="/media/images/cross.png" />Enter a valid e-mail address.</label>');
	}
}

