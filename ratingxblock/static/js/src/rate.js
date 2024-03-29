/* Javascript for RateXBlock. */
// Work-around so we can log in edx-platform, but not fail in Workbench
if (typeof Logger === 'undefined') {
    var Logger = {
        log: function(a, b) { 
	    console.log("<<Log>>"); 
	    console.log(a);
	    console.log(b);
	    console.log("<</Log>>"); 
	}
    };
}

function RatingXBlock(runtime, element) {
    var feedback_handler = runtime.handlerUrl(element, 'feedback');

    $(".rate_submit_feedback", element).click(function(eventObject) {
	var freeform = $(".rate_freeform_area", element).val().trim();
	var vote = 0;

	if ($(".fa.fa-star.checked", element).length === 0) {
	    vote = -1;
	} else {
	    vote = parseInt($(".fa.fa-star").index($(".fa.fa-star.checked")));
	}
	var feedback = {"freeform": freeform, 
		    "vote": vote};
	Logger.log("edx.ratexblock.submitted", feedback);
	$.ajax({
            type: "POST",
            url: feedback_handler,
            data: JSON.stringify(feedback),
	    success: function(data) {$('.rate_thank_you').text(data.response);}
        });
    });

	activeVote();
	activeStar()

    // $('.rate_radio', element).change(function(eventObject) {
	// var target_id = eventObject.target.id;
	// var vote = parseInt(target_id.split('_')[1]);
	// Logger.log("edx.ratexblock.likert_clicked", {"vote":vote});
    // });

    // $('.rate_freeform_area', element).change(function(eventObject) {
	// var freeform = eventObject.currentTarget.value;
	// Logger.log("edx.ratexblock.freeform_changed", {"freeform":freeform});
    // });

}


function updateRating(data) {
	$('.rate_thank_you').text(data.response);
}


function activeVote() {
	$(document).on('click', '.fa.fa-star', function() {
		let parentItem = $(this).parents('.star');
		parentItem.addClass('selected')
		parentItem.find('.fa.fa-star').removeClass('checked');
		$(this).addClass('checked');
	})
}

function activeStar() {
	$('.star').each(function() {
		if($(this).find('.fa.fa-star.checked').length > 0) {
			$(this).addClass('selected')
		} else {
			$(this).removeClass('selected')
		}
	})
}
