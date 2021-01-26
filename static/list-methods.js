const BASE_URL = "/"

/**
 * This class controls the creation of new epic lists, and the updating of already
 * instantiated lists. It directly interacts with the back end to instantiate and update
 * lists.
 */

class List {
    constructor(characters, title, user_id, is_ranked, is_private, story_id) {
        this.characters = characters;
        this.title = title;
        this.user_id = user_id;
        this.is_ranked = is_ranked;
        this.is_private = is_private;
        this.story_id = story_id;
    }


    /**
     * Creates a new list instance
     * 
     * Sends a POST request to backend to save characters and takes response to
     * create new list
     */

    static async create(characters) {
        const response = await axios.post(BASE_URL + "/lists/new", {
            list: {
                characters
            }
        })

        const newList = new List(
            response.data.characters,
            response.data.title,
            response.data.user_id,
            response.data.ranked,
            response.data.private,
            response.data.story_id
        )

        return newList;
    }




}