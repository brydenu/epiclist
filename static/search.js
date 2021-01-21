// Tools for searching the Giantbomb API when creating/updating lists

const searchField = document.getElementById("character-name");
const searchButton = document.getElementById("search-btn");
const KEY_AND_FORMAT = "?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json";
const URL = "http://giantbomb.com/api";
const TO_BACKEND = "/search-characters";



async function searchForCharacter(char_name) {
    const api_query = URL + "/search" + KEY_AND_FORMAT + "&query=" + char_name + "&resources=character";
    const query = {
        "query": api_query
    };
    const data = JSON.stringify(query);
    console.log(data)
    const res = await axios.post(TO_BACKEND, { data })
    console.log(res)
};

searchForCharacter('link');