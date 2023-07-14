from flask import Flask, request, jsonify
from search import search
import html
from filter import Filter
from storage import DBStorage

app = Flask(__name__)

styles = """
<style>

.site {
    font-size: .8rem;
    color:black;
}

.snippet{
font-size: .9rem;
color: black;
margin-bottom: 30px;
}

body {
    background-image: linear-gradient(to right, #f5ce62, #e43603, #fa7199, #e85a19);
    box-shadow: 0 4px 15px 0 rgba(229, 66, 10, 0.75);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    justify-content: space-around;
}

form {

    background-image: linear-gradient(to right, #29323c, #485563, #2b5876, #4e4376);
    box-shadow: 0 4px 15px 0 rgba(45, 54, 65, 0.75);
    width: 1000px;
    border: 3px solid white;
    padding: 20px;
    color: white;
    border-radius: 20px;


}

.rel-button{
    cursor: pointer;
    color: red;
}

</style>
<script>
const relevant = function(query, link){
    fetch("/relevant",{
        method: 'POST',
        headers: {
            'Accept' : 'application/json',
            'Content-Type' : 'application/json'
        },
        body: JSON.stringify({
            "query" : query,
            "link" : link
        })
    });
    
    }
    </script>
"""

search_template =styles + """
<body>
<style contenteditable 
style="display: block;
white-space: pre;">
html{
background: #BADA55;
}
</style>
<title>Alex Will Find It</title>
<h1>Type it in, Alex will find it!</h1>

<form action="/" method="post">
    <input type="text" name="query">
    <input type="submit" value="Search">

</form>

</body>
"""

result_template = """
    <p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}", "{link}");'>Relevant</span></p>
    <a href="{link}">{title}</a>
    <p class="snippet">{snippet}</p>
"""

def show_search_form():
    return search_template

def run_search(query):
    results = search(query)
    fi = Filter(results)
    results = fi.filter()
    rendered = search_template
    results["snippet"] = results["snippet"].apply(lambda x: html.escape(x))
    for index, row in results.iterrows():
        rendered+= result_template.format(**row)
    return rendered


"127.0.0.1:5001"
"flask --debug run --port 5001"

@app.route("/", methods=["GET", "POST"])
def search_form():
    if request.method == "POST":
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()
    

@app.route("/relevant", methods=["POST"])
def mark_relevant():
    data=request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query,link, 10)
    return jsonify(success=True)