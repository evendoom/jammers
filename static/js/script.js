$(document).ready(function() {
    // Dropdown menu for mobile
    $('.dropdown-trigger').dropdown({
        constrainWidth: false
    });
    
    // Modal for messages and feedback
    $('.modal').modal();

    // Resize textbox for sending message modal
    $('.autoResize').on('input', function() {
        this.style.height = '100px';
        this.style.height = (this.scrollHeight) + 'px';
    });
});
