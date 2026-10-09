fn(read_text(path)) {
    input := file(path)
    input.open("r")
    text := input.read()
    input.close()
    return text
}

styles := read_text("public/styles.css")
script := read_text("public/frontend-js.js")
image := read_text("public/images.svg")
data := {"styles": "styles.css", "script": "frontend-js.js", "image": "images.svg", "css_length": styles.length(), "js_length": script.length(), "image_length": image.length()}
out := file(getenv("NIFT_HOOK_OUTPUT"))
out.open("w")
out.write(data.stringify())
out.save()
out.close()
