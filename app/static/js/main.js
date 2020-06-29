// questions count in navbar 
function set_questions_count(n) {
  $('#question_count').text(n);
  $('#question_count').css('visibility', n ? 'visible' : 'hidden');
}