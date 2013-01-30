var updateChart =  function(pId) {
  	return function(dateTxt, inst) {
		$(".validation-err-msg").css("visibility", "hidden");
		var fromDt = null;
		var toDt = null;	
		var pDate = $(pId).datepicker("getDate");
		if (pDate == null) {
			return;
		}
		var pDateTxt = $.datepicker.formatDate('yy-mm-dd',pDate);
		try {
			var mDate = $.datepicker.parseDate('yy-mm-dd', dateTxt); 
			var pDate = $.datepicker.parseDate('yy-mm-dd', pDateTxt); 
			fromDt = (pId == "#dateFrom" ? pDateTxt : dateTxt);
			toDt = (pId == "#dateFrom" ? dateTxt : pDateTxt);
			if ($.datepicker.parseDate('yy-mm-dd',fromDt) > $.datepicker.parseDate('yy-mm-dd',toDt)) {
				throw "Invalid date range";
			}
		} catch (e) {
			$(".validation-err-msg").css("visibility", "visible");
			return;
		}
		location.assign(location.pathname + "?from=" + fromDt + "&to=" + toDt);		
		$(this).blur();
	}
};
var imgW = 500;
var imgH = 400;
$(document).ready(function() {
  $("#dateFrom").datepicker({
         dateFormat: "yy-mm-dd", 
         changeMonth: true, 
         changeYear: true, 
         showButtonPanel: false,
	   onSelect:updateChart('#dateTo')
     });
$("#dateTo").datepicker({
         dateFormat: "yy-mm-dd", 
         changeMonth: true, 
         changeYear: true, 
         showButtonPanel: false,
	   onSelect:updateChart('#dateFrom')
     });
imgW =  Math.floor($(".reportImages").parent().innerWidth() / 2 - 100);  
jQuery.each($('.reportImages').find('img').map(function(){return this}).get(), function(idx,elem){elem.src=elem.src+"&w="+imgW+"&h="+imgH});
});  