(function($){
	$(function(){

		$('.button-collapse').sideNav();
		$('select').material_select();
		$('.datepicker').pickadate({
            selectMonths: true,
            selectYears: 15,
            format: 'dd/mm/yyyy'
        });

		$('.modal-trigger').leanModal();

		$('#is_capital').click(function() {
		    if ($(this).is(':checked')) {
		        $('#nearest_capital').hide();
		        $('#capital_id').prop('selectedIndex', 0);
		        $('#capital_id').removeAttr('required');
		    } else {
		        $('#nearest_capital').show();
		        $('#capital_id').attr('required', 'true');
		    }
		});

  }); // end of document ready
})(jQuery); // end of jQuery name space