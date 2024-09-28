from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/watch")
def watch():
    stream_link = request.args.get("stream_link")
    return render_template("Watch.html", stream_link=stream_link)


def run():
    app.run(host="0.0.0.0", port=5000, debug=False)
