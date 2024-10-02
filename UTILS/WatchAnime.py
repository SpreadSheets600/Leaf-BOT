from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/watch")
def watch():
    stream_link = request.args.get("stream_link")
    subtitles = request.args.getlist("subtitles")
    thumbnails_url = request.args.get("thumbnails_url")
    intro_start = request.args.get("intro_start")
    intro_end = request.args.get("intro_end")
    outro_start = request.args.get("outro_start")
    outro_end = request.args.get("outro_end")

    return render_template(
        "Watch.html",
        stream_link=stream_link,
        subtitles=subtitles,
        thumbnails_url=thumbnails_url,
        intro_start=intro_start,
        intro_end=intro_end,
        outro_start=outro_start,
        outro_end=outro_end,
    )

def run():
    with app.app_context():
        app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    from threading import Thread

    server_thread = Thread(target=run)
    server_thread.start()
