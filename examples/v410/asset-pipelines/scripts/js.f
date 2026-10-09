fn(read_text(path)) {
    input := file(path)
    input.open("r")
    text := input.read()
    input.close()
    return text
}

source := read_text("src/js/base.js") + "\n" + read_text("src/js/app.js")
result := minify(source, "js")
if(!result.ok) { throw error(result.error, "build.minify_failed") }
out := file(getenv("NIFT_HOOK_OUTPUT"))
out.open("w")
out.write(result.output)
out.save()
out.close()
