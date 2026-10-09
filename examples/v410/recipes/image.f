result := cmd("magick", "src/images/hero.png", getenv("NIFT_HOOK_OUTPUT")).cwd(getenv("NIFT_HOOK_ROOT")).run()
if(!result.launched || result.exit_code != 0) {
    throw error("Image encoding failed: " + result.stderr, "build.tool_failed")
}
