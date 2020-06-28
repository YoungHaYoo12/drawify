// Ajax request if "Add Drawing" button clicked
$('.draw-buttons').click(
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
       console.log('SUCCESS')
     }
    }
  )
  }
)

// hide navbar 
$('nav').hide();