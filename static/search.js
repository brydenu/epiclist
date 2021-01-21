// Tools for searching the Giantbomb API when creating/updating lists

const searchField = document.getElementById("character-name");
const searchButton = document.getElementById("search-btn");
const searchResults = document.getElementById("search-results");
const KEY_AND_FORMAT = "?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json";
const URL = "http://giantbomb.com/api";
const TO_BACKEND = "/search-characters";
const FIELDS = "&resources=character&limit=10"



// This combines the constants above into a search query that will be sent to the back-end
// The back-end will query the API and return a response with specific attributes
async function searchForCharacter(char_name) {
    const api_query = URL + "/search" + KEY_AND_FORMAT + "&query=" + char_name + FIELDS;
    const query = {
        "query": api_query
    };
    const data = JSON.stringify(query);

    const res = await axios.post(TO_BACKEND, { data });

    let whatever = await handleResponse(res)
    return whatever;
};

// Called in searchForCharacter
// Takes response object and displays character results from it on screen
function handleResponse(res) {
    const data = res["data"]["character_results"];
    console.log(data);
    console.log(data[0]["name"])

    searchResults.innerHTML = "";
    searchResults.innerHTML = `<div class="list-group" id="list-results"></div>`;

    // Create button elements to be list group items in search results. Each button will have a button inside
    // that can be clicked to add the character to the list the user is making.
    for (let i = 0; i < data.length; i++) {
        let btnContent = `<button type="button" class="list-group-item list-group-item-action">
        <img src="${data[i]["image_url"]}" alt="Picture of ${data[i]["name"]}"> ${data[i]["name"]}
        <span class="pull-right"><span class="btn btn-sm btn-primary add-btn" id="${data[i]["api_id"]}">Add</span></span></button>`;
        let btn = document.createElement("button");
        btn.innerHTML = btnContent;
        searchResults.appendChild(btn.childNodes[0]);
    }
}



searchForCharacter('mario');