result := cmd("./node_modules/.bin/esbuild", "src/js/app.ts",
              "--bundle", "--outfile=" + getenv("NIFT_HOOK_OUTPUT")).cwd(getenv("NIFT_HOOK_ROOT")).run()
if(!result.launched || result.exit_code != 0) {
    throw error("Bundler failed: " + result.stderr, "build.tool_failed")
}
