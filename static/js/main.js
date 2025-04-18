const spinner = document.querySelector(".spinner");
const body = document.querySelector("body");


function loading() {
   spinner.style.visibility = 'visible';
   body.style.overflow = 'hidden';
}
window.onpageshow = function(event) {
    if (event.persisted) {
          body.style.overflow = 'auto';
    spinner.style.visibility = 'hidden';
    }
 }

	function searchTable() {
		var input, filter, table, rows, cells, i, j, cell, matchFound;
		input = document.getElementById("searchInput");
		filter = input.value.toLowerCase();
		table = document.querySelector("table");
		rows = table.querySelectorAll("tbody tr");
		clearSearchButton = document.getElementById("clearSearchButton");
		if (input.value.length > 0) {
			clearSearchButton.classList.remove("hidden");
		} else {
			clearSearchButton.classList.add("hidden");
		}
		for (i = 0; i < rows.length; i++) {
			cells = rows[i].querySelectorAll("td");
			matchFound = false;
			
			for (j = 0; j < cells.length; j++) {
				cell = cells[j];
				if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
					matchFound = true;
					break;
				}
			}
			
			if (matchFound) {
				rows[i].classList.remove("hidden");
			} else {
				rows[i].classList.add("hidden");
			}
		}
	}
	
	function clearSearch() {
		var input = document.getElementById("searchInput");
		input.value = '';
		searchTable(); 
	}
