// read more collapse
document.querySelectorAll('.read-more').forEach(function(item) {
  item.addEventListener('click', function(event) {
      event.preventDefault(); // Prevent the default behavior of the link
      var qaAnswer = this.parentElement.querySelector('.qa-answer-box').querySelector('.qa-answer');
      qaAnswer.classList.toggle('expanded');
      this.classList.toggle('collapsed');
      if (this.classList.contains('collapsed')) {
          this.innerHTML = '- Read Less';
      } else {
          this.innerHTML = '+ Read More';
      }
  });
});