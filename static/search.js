// Tools for searching the Giantbomb API when creating/updating lists

const searchField = document.getElementById("character-name");
const searchButton = document.getElementById("search-btn");
const searchContainer = document.getElementById("search-results");
const listContainer = document.getElementById("list-container");
const KEY_AND_FORMAT = "?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json";
const URL = "http://giantbomb.com/api";
const TO_BACKEND = "/search-characters";
const FIELDS = "&resources=character&limit=10";
const FOR_SEARCH = "search";
const FOR_LIST = "list";

let currentSearch = [];
let currentList = [];



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
    searchContainer.addEventListener('click', handleAdd);
};


// Create button elements to be list group items in search results. Each button will have a button inside
// that can be clicked to add the character to the list the user is making.
function makeListGroupHTML(data, location) {
    for (let i = 0; i < data.length; i++) {
        const btnContent = `<button type="button" class="list-group-item list-group-item-action" data-index="${i}">
        <img src="${data[i]["image_url_lg"]}" alt="Picture of ${data[i]["name"]}" class="search-char-image"> ${data[i]["name"]}
        <span class="btn btn-sm btn-primary add-btn">Add</span></button>`;
        const btn = document.createElement("button");
        btn.innerHTML = btnContent;
        if (location == FOR_SEARCH) {
            searchContainer.appendChild(btn.childNodes[0]);
            currentSearch.push(data[i]);
        } else if (location == FOR_LIST) {
            listContainer.appendChild(btn.childNodes[0]);
        }
    }
}

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
        const btn = evt.target.closest("button");
        const arrIndex = btn.dataset.index;

        currentList.push(currentSearch[arrIndex]);
        showList();
    }
};


// Shows current list
function showList() {
    listContainer.innerHTML = "";
    listContainer.innerHTML = `<div class="list-group" id="current-list"></div>`;

    makeListGroupHTML(currentList, FOR_LIST);
}


searchButton.addEventListener("click", handleSearch);







