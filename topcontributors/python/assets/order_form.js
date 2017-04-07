// This file contains JavaScript code used by the Bundle Order Form (bundle.html)
(function(){
  'use strict';

  var $orderform = $('form.order-form');

  // Override the order form's submit handler to do an AJAX submit
  $orderform.submit(function(event) {
    event.preventDefault();
    $.ajax({
      type: $orderform.attr('method'),
      url: $orderform.attr('action'),
      data: $orderform.serialize(),
      dataType: 'json',
      error: function() {
        alert('Error communicating with the server, or the server had a 500 Internal Server Error!');
      },
      success: function(response) {
        $('p.order-results').hide();
        if (response.success) {
          $('p.order-results.success').text(response.message).show();
        } else {
          $('p.order-results.error').text(response.message).show();
        }
      }
    });
  });

})();