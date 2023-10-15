const TagCardSearch = document.getElementById("card_search");
const updatesOrCards = document.getElementById("new_updates");

function toggleCard() {
  updatesOrCards.innerHTML = '';

  var searchingBar = document.createElement("div");
  searchingBar.classList.add("form-floating");

  var searchingInput = document.createElement("textarea");
  searchingInput.classList.add("form-control");
  searchingInput.id = floatingTextarea;
  searchingInput.placeholder = "Search for a card here";
  
  var searchingLabel = document.createElement("label");
  searchingLabel.htmlFor = "floatingTextarea"; 
  searchingLabel.innerText = "Card"; 

  searchingBar.appendChild(searchingInput);
  searchingBar.appendChild(searchingLabel);

  // add into html element
  updatesOrCards.appendChild(searchingBar);

  
};

// <div class="form-floating">
//   <textarea class="form-control" placeholder="Leave a comment here" id="floatingTextarea"></textarea>
//   <label for="floatingTextarea">Comments</label>
// </div>

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