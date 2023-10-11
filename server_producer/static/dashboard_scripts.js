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
