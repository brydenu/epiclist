All characters come from the GiantBomb API: https://www.giantbomb.com/api/

# EpicList 

(https://epiclists.herokuapp.com)

___

### What is EpicList?   

EpicList is meant work as a combinaton of Pinterest and Twitter, but directed at video game enthusiasts who are passionate about their viewpoints of the subjective strengths, weaknesses, advantages, disadvantages and/or more of their favorite characters.   

Users can create lists based on whatever they desire, such as who is the strongest, fastest, funniest, coolest, character in the group. These lists can be ranked and unranked, allowing for users to simply pool a group of characters together arbitrarily, or be more intentional with character placements in a ranked list. These lists can be edited in many ways, such as adding characters later on, removing characters in the list, and/or switching a list between public and private, or ranked and unranked.   

Beyond making lists, users can follow/unfollow other users via seeing their lists in the main feed, going to the other user's profile and following them. Once a user is following another user, they can choose to switch their main feed between seeing all public lists being created, and seeing only lists of those they are following. If a list is set to private by a user, only they will be able to see it until the list is made public. Users can see their own private lists via a link on their own profile.   

Users can update their own information that may be seen on their profile including username, bio, profile image, and their favorite character.   

___

### How Does it Work?   

EpicList draws its characters from the GiantBomb.com API. This API allows end-users to search for characters on EpicList, which sends a GET request querying the GiantBomb character search to respond with any results. The results are sent back to EpicList where they are displayed for the user to pick from.   

Once a user submits a list of characters, EpicList initializes each character from the list. If the character already exists in the database, the information for the character will be pulled from the database and be displayed for users. If the character has not been used before, and therefore not in the database, EpicList will send a query to GiantBomb which will return the full information of the character. The information is then parsed for only the properties needed, which are saved to the database as a new character.   

___

### Standard User Flow

As a new user, you will be directed to a home page welcoming you to the site, and asking you to log in or register. Either option takes you to a formn requesting a username and password, while registering also asks for an image URL if desired (this is optional, and if omitted the user's profile picture will be a default). It is worth noting that when not signed in, the only page user can see is the log in, register, register home, or individual list pages. This is so in the scenario in which someone wanted to show a friend who does not have an account a list, they could send a link of the list and the friend could see just that list and nothing else.   

Once logging in, you are then taken to an index page showing all recently made public lists by all users. This page also shows information about the current user. This information includes total number of public lists, the user's favorite character if they have one, number of followers of the user, and the number of people the user is following. This page also includes an option underneath the "Lists" title to switch between all lists and lists made by people the user follows, if they are following anyone. All of these lists are limited to the first four characters, and any list longer than this is shortened on this page with an ellipses.   

When clicking on the title of each list, you are taken to a page showing a larger version of each list, with all characters shown (as opposed to the maximum of four characters shown on the index page). If the user created this list, they will see buttons under the title to edit or delete this list. The author of the list is also credited under the title, with the name being a link to the author's page.   

Once at another user's profile page, signed in user can follow or unfollow the user whose profile they are at, as well as see all public lists made by that user. Also visible are the profile user's public information, including their favorite character, number of followers, number of people they are following, number of public lists made, and a bio.

If a user goes to their own page they will see very similar things, although they will not see a follow button, and will see some extra links. The first extra link is located in the information panel and will take the user to an edit information screen, where the user can update any information noted above. The other link is located at the top of their own lists jumbotron, and will take the user to see all of their own private lists on a seperate page. Even if another user types the URL of the link in, they will not get access unless their credentials are those of the user who made the private lists.

The navbar at the top of the screen has a button that will take the user to the create list page. This page is split into two sides. The left side is meant for searching for characters to add to the list, while the right side allows you to name the list, check if the list will be private or public, and ranked or unranked, while also showing the characters currently in the list. There are add and remove buttons on the character items from the search side and current list side respectively. If the ranked box is checked, arrows will appear on the current list side on each character item, along with ranks. When interacted with, these arrows will move characters up and down rank depending on the arrow direction clicked. Once the list is submitted the user is then taken to the index, where they should see their created list.

___

### Technology Stack

This project uses a few different technologies throughout its functionality. These technologies are listed below.

Languages:

- PostgresQL
- Python
- JavaScript
- HTML
- CSS

Libraries/Frameworks:

- Bootstrap
- Flask
- Bcrypt
- SQLAlchemy
- WTForms


