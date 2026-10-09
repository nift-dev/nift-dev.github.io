result := cmd("sass", "src/styles/main.scss", getenv("NIFT_HOOK_OUTPUT")).cwd(getenv("NIFT_HOOK_ROOT")).run()
if(!result.launched || result.exit_code != 0) {
    throw error("Sass failed: " + result.stderr, "build.tool_failed")
}
optimized := minify(getenv("NIFT_HOOK_OUTPUT"), {"in_place": true})
if(!optimized.ok) { throw error(optimized.error, "build.minify_failed") }
