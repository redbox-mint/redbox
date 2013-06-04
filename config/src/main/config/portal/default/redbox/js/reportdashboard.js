var updateChart =  function(pId) {
  	return function(dateTxt, inst) {
		$(".validation-err-msg").css("visibility", "hidden");
		var fromDt = null;
		var toDt = null;	
		var pDate = $(pId).datepicker("getDate");
		if (pDate == null) {
			return;
		}
		var pDateTxt = $.datepicker.formatDate('d/m/yy',pDate);
		try {
			var mDate = $.datepicker.parseDate('d/m/yy', dateTxt); 
			var pDate = $.datepicker.parseDate('d/m/yy', pDateTxt); 
			fromDt = (pId == "#dateFrom" ? pDateTxt : dateTxt);
			toDt = (pId == "#dateFrom" ? dateTxt : pDateTxt);
			if ($.datepicker.parseDate('d/m/yy',fromDt) > $.datepicker.parseDate('d/m/yy',toDt)) {
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
         dateFormat: "d/m/yy", 
         changeMonth: true, 
         changeYear: true, 
         showButtonPanel: false,
	   onSelect:updateChart('#dateTo')
     });
$("#dateTo").datepicker({
         dateFormat: "d/m/yy", 
         changeMonth: true, 
         changeYear: true, 
         showButtonPanel: false,
	   onSelect:updateChart('#dateFrom')
     });
imgW =  Math.floor($(".reportImages").parent().innerWidth() / 2 - 120);  
jQuery.each($('.reportImages').find('img').map(function(){return this}).get(), function(idx,elem){elem.src=elem.src+"&w="+imgW+"&h="+imgH});
});  