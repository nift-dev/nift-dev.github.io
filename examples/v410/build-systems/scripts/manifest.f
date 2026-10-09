fn(read_text(path)) {
    input := file(path)
    input.open("r")
    text := input.read()
    input.close()
    return text
}

app := read_text("public/app-js.js")
data := {"app": "app-js.js", "length": app.length()}
out := file(getenv("NIFT_HOOK_OUTPUT"))
out.open("w")
out.write(data.stringify())
out.save()
out.close()
