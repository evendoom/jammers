// Dropdown menu for mobile
$(document).ready(function() {
    $(".dropdown-trigger").dropdown();   
});

// Modal for feedback
$(document).ready(function(){
    $('.modal').modal();
});

// Resize textbox for sending message modal
$(document).ready(function() {
    $('#sendMessage').on('input', function() {
        this.style.height = '100px';
        this.style.height = (this.scrollHeight) + 'px';
    });
});
