$('.questions-question-wrapper li').hide();
$('.hint-hide-btn').hide();

$('.hint-view-btn').each(
  function() {
    $(this).on("click", () => {
      $(this).siblings('li').show();
      $(this).siblings('.hint-hide-btn').show();
      $(this).hide();
    })
  }
)

$('.hint-hide-btn').each(
  function() {
    $(this).on("click", () => {
      $(this).siblings('li').hide();
      $(this).siblings('.hint-view-btn').show();
      $(this).hide();
    })
  }
)