// Countdown Timer
$(document).ready(function() {
    $(".product_countdown-timer").each(function() {
        var $this = $(this);
        var endTime = $this.data('countdown');
        
        // Initialize countdown
        $this.countdown(endTime, function(event) {
            var format = '%D days %H:%M:%S';  // Show days, hours, minutes, and seconds
            $(this).text(event.strftime(format));
        }).on('finish.countdown', function() {
            // Reload the page when countdown ends
            location.reload();
        });
    });
}); 