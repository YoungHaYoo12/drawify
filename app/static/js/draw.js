// Ajax request if "Add Drawing" button clicked
$('.add-button').click(
  () => {
    const canvas = $('#canvas')[0];
    
  $.ajax(
    {
      url:'/drawings/add',
      type: 'POST',
      data: {
        dataURL:canvas.toDataURL()
      }
    }
  )
  .done(
    function(data) {
     if (data.result == 'success') {
       console.log('SUCCESS');
       $('#successModal').modal('show');
     }
    }
  )
  }
)

// hide navbar 
$('nav').hide();

// hide background image
$('body').css({'background-image':'none'});

// add href links to buttons 
var link = "/";
$('.home-button').attr('href',link);
var link = "/drawings/list";
$('.my-drawings-button').attr('href',link);