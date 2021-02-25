// Tools for searching the Giantbomb API when creating/updating lists

const searchField = document.getElementById("character-name");
const searchButton = document.getElementById("search-btn");
const searchContainer = document.getElementById("search-results");
const listContainer = document.getElementById("list-container");
const submitBtn = document.getElementById("submit-btn");
const formCharacters = document.getElementById("characters");
const KEY_AND_FORMAT = "?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json";
const URL = "http://giantbomb.com/api";
const TO_BACKEND = "/search-characters";
const FIELDS = "&resources=character&limit=10";
const FOR_SEARCH = "search";
const FOR_LIST = "list";

let ranked_check = document.getElementById("is_ranked")
let currentSearch = [];
let currentList = [];


/********************* SEARCHING *********************/

// This combines the constants above into a search query that will be sent to the back-end
// The back-end will query the API and return a response with specific attributes
async function searchForCharacter(char_name) {
    const api_query = URL + "/search" + KEY_AND_FORMAT + "&query=" + char_name + FIELDS;
    const query = { "query": api_query };
    const data = JSON.stringify(query);

    const res = await axios.post(TO_BACKEND, { data });

    handleResponse(res)
};


// Called in searchForCharacter
// Takes response object and displays character results from it on screen
function handleResponse(res) {
    currentSearch = [];
    const data = res["data"]["character_results"];
    showResults(data);
};


// Adds HTML of the results from searching for characters
function showResults(data) {

    searchContainer.innerHTML = "";
    searchContainer.innerHTML = `<div class="list-group" id="list-results"></div>`;

    makeListGroupHTML(data, FOR_SEARCH);
};

// Shows current list
function showList() {
    listContainer.innerHTML = "";
    listContainer.innerHTML = `<div class="list-group" id="current-list"></div>`;

    makeListGroupHTML(currentList, FOR_LIST);
};


// Create button elements to be list group items in search results. Each button will have a button inside
// that can be clicked to add the character to the list the user is making.
function makeListGroupHTML(data, location) {

    for (let i = 0; i < data.length; i++) {

        let btnClass = null;
        let btnTitle = null;

        // If list is being implemented for search, an "add" button should appear
        // If list is being implemented for current list, a "remove" button should appear
        if (location == FOR_SEARCH) {
            btnClass = "btn-primary add-btn";
            btnTitle = "Add";
        } else if (location == FOR_LIST) {
            btnClass = "btn-danger remove-btn";
            btnTitle = "Remove";
        };

        let arrows = "";
        let rank = "";
        if (ranked_check.checked && location == FOR_LIST) {
            arrows = `<span class="arrow-btns float-right col-1" style="font-size:1.5em; color:lightblue;"><i class="fas fa-caret-square-up m-2"></i><i class="fas fa-caret-square-down m-2"></i></span>`;
            rank = `<p class="display-4 col-1 float-left">${i + 1}</p>`;
        }

        // Creates necessary HTML for a list-group, with appropriate properties
        // for each search result taken from attributes from the response object
        // Uses location param to decide which button to tack on, and where to put the element
        const divContent = `<div class="list-group-item list-group-item-action row list-character justify-content-between" data-index="${i}">${rank}
        <img src="${data[i]["image_url"]}" alt="Picture of ${data[i]["name"]}" class="col-8 search-char-image"> ${data[i]["name"]}
        <button class="btn btn-sm ${btnClass}">${btnTitle}</button>${arrows}</div>`;
        const div = document.createElement("div");
        div.innerHTML = divContent;
        if (location == FOR_SEARCH) {
            searchContainer.appendChild(div.childNodes[0]);
            currentSearch.push(data[i]);
        } else if (location == FOR_LIST) {
            listContainer.appendChild(div.childNodes[0]);
        }
    }

    // Adds event listeners to the lists to listen for a new add or remove
    searchContainer.addEventListener('click', handleAdd);
    listContainer.addEventListener('click', handleRemove)
}

/************ EVENT HANDLERS ************************/

// Function to listen for clicks of the search button and calls searchForCharacter with
// inputs from search field
async function handleSearch(evt) {
    evt.preventDefault();
    searchVal = searchField.value;
    await searchForCharacter(searchVal);
};


// Function to listen for clicks on character add buttons
// If clicked, add corresponsing character to the list
function handleAdd(evt) {
    evt.preventDefault();

    // Should only work if the clicked element is an add button
    classes = [...evt.target.classList];
    if (classes.includes('add-btn')) {
        const div = evt.target.closest("div");
        const arrIndex = div.dataset.index;

        char = currentSearch[arrIndex];

        currentList.push(char);
        formCharacters.value = toForm(currentList);

        showList();
    }
};

function handleMove(evt) {
    const classes = [...evt.target.classList];
    const div = evt.target.closest("div");
    const arrIndex = div.dataset.index;

    char = currentList[arrIndex];

    if (classes.includes("fa-caret-square-up")) {
        currentList.splice(arrIndex, 1)
        currentList.splice((arrIndex - 1), 0, char)
    } else if (classes.includes("fa-caret-square-down")) {
        currentList.splice(arrIndex, 1)
        currentList.splice((arrIndex + 1), 0, char)
    }

    formCharacters.value = toForm(currentList);
    showList();

}


// Function to listen for clicks on "remove button" on characters
// that are already in the list. Should remove them from the UI and 
// remove them from the array.
function handleRemove(evt) {
    evt.preventDefault()

    classes = [...evt.target.classList];
    if (classes.includes('remove-btn')) {
        const div = evt.target.closest("div");
        const arrIndex = div.dataset.index;

        if (currentList.length < 2 && arrIndex == 0) {
            currentList = [];
            formCharacters.value = "";
        } else {
            currentList.splice(arrIndex, 1);
            formCharacters.value = toForm(currentList);
        }

        showList();
    }
}

// Converts currentList to a string that can input to the hidden characters field
function toForm(currList) {
    let guidString = currList[0]["guid"];
    for (let i = 1; i < currList.length; i++) {
        guidString = guidString + ", " + currList[i]["guid"];
    }
    return guidString;
}



// Function for handling when the checkbox of "ranked" is switched on.
// When on, show ranks and arrows to change ranks
// When off, remove ranks and remove arrows
function handleRankedCheckbox() {

    const arrowContainer = document.getElementsByClassName("arrow-btns")

    if (ranked_check.checked) {
        const arrows = `<span class="arrow-btns float-right" style="font-size:2em; color:lightblue;"><i class="fas fa-caret-square-up m-2"></i><i class="fas fa-caret-square-down m-2"></i></span>`;
        for (characterButton of arrowContainer) {
            characterButton.innerHTML = arrows;
        }
    } else {
        for (characterButton of arrowContainer) {
            characterButton.innerHTML = "";
        }
    }
    formCharacters.value = toForm(currentList);
    showList()
}

// If user is editing an already made list, this function will fill the 
// characters side with the characters in the list
async function fillListForEdit() {
    if (window.location.href.includes("edit")) {
        const listId = document.getElementById("edit-list-title").dataset.listid;

        const req = await axios.get(`/get-list/${listId}`)
        characters = req.data.characters
        console.log(characters)
        for (char of characters) {
            currentList.push(char)
        }
        formCharacters.value = toForm(currentList);
        showList()
    }

}

listContainer.addEventListener("click", handleMove);
searchButton.addEventListener("click", handleSearch);
ranked_check.addEventListener("click", handleRankedCheckbox);
fillListForEdit();




