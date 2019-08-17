# Items here will be displayed through the help command
descriptions = {
    "default": {
        "help": "Pulls up this message",
        "ping": "Responds with 'pong!', used to check response time of the bot.",
        "someone": "Mentions a random user with a message.",
        "vrole": "Vanity roles. Provides options for roles that a user can assign themselves without the need of a 'Manage Roles' permission. Available roles can be configured by an admin. (options: add, remove, request, revoke, list)"
    },

    "fun": {
        "madlib": "Walks you through a fill-in-the blank story.",
        "markov": "Generates a Markov Chain from recent messages.",
        "trope": "Searches Stack Overflow and returns the top result.",
        "stack": "Returns a random tv tropes page."
    },

    "overlay": {
        "overlays": "Lists available overlay commands."
    },

    "utility": {
        "countdown": "Starts a countdown timer that the bot updates in real time. Each server is limited to one timer at a time. \ne.g. *\"c|countdown title 01:30:05 #23272A -m\"* (including `-m` makes it mention everyone once finished)",
        "invite": "Creates a fancy embedded invite card for people to react to as a way to RSVP for an upcoming event. For syntax information, trigger the command without any arguments."
    },

    "admin": {
        "cherrypick": "Selectively purges messages containing specific keywords. \nThe different modes will delete messages with **any**, or **all** the listed keywords (user mention in place of a mode defaults to any).\ne.g *\"c|cherrypick any 25 lasagna\"* (the number is how many messages to ***check*** the keyword for, not how many you want to delete)"
    }
}
