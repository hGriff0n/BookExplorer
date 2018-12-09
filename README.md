## BookExplorer

# Goal

The end goal of this project is to produce an engine that is capable of recommending books to the user that "expand" (and "complement") on their existing library. The primary goal is of expansion: If the user has no books on a topic A, then books on A should be recommended by the engine. A second goal would to mimic the process of innovative discovery, where recommendations are tailored to exist "near" the user's existing library. A tertiary goal would be to find synergistic recommendations: If the user has books on history, and books on mathematics, then a book on the history of mathematics should be recommended. A quaternary goal would be to incorporate broad public opinion into the ranking results, allowing for "discussion books" to enter into the user's recommendations, even if they lay outside their normal consideration.

Ideally this engine should operate as an broadening force on the user's library, making it easier to discover and explore new topics outside of their normal interest areas ("under-explored"). This engine should also be focused on providing positive pressures; above all the tool should enrich the life and reading experiences of the user.

# Approach

The process for translating user data will be split into three broad stages: input frontend, ml engine, output frontend. The frontends are responsible for collecting data about the user's current library and transforming it into data that the ml engine can operate on, in a manner that most efficiently utilizes the api which stores the user's library information. The ml engine would then be responsible for reducing and mapping the provided library information unto the "global knowledge graph" and selecting a list of interesting "topics" to consider. These topics are the "recommendations" that the engine considers would be serve the user according to the goals outline above. The output frontend is then responsible for communicating these results to the end user in a way it best sees fit. Any recommendations of specific books would be handled in this layer as the nature of the ml-engine (knowledge graph) makes it ill suited to extract the necessary information.
