fn(read_text(path)) {
    input := file(path)
    input.open("r")
    text := input.read()
    input.close()
    return text
}

source := "const api = " + read_text("public/generated-api.json") + ";\nconsole.log(api.message);\n"
result := minify(source, "js")
if(!result.ok) { throw error(result.error, "build.minify_failed") }
out := file(getenv("NIFT_HOOK_OUTPUT"))
out.open("w")
out.write(result.output)
out.save()
out.close()
