#!/usr/bin/env python3
"""Execute the built About-page template example with the supplied Nift binary."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent

class Sample(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inside = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'code' and any(key == 'data-about-template' for key, _ in attrs):
            self.inside = True

    def handle_endtag(self, tag):
        if tag == 'code':
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nift', type=Path, default=ROOT.parent / 'nift/nift')
    args = parser.parse_args()
    binary = args.nift.resolve()
    if not binary.is_file():
        parser.error('Build the supplied Nift source first, or specify --nift.')
    sample = Sample()
    sample.feed((ROOT / 'public/about.html').read_text())
    code = ''.join(sample.parts)
    assert code.startswith('@for(post : posts) {'), 'Incorrect loop syntax'
    with tempfile.TemporaryDirectory(prefix='nift-about-example-') as temp:
        project = Path(temp)
        for directory in ('.nift', 'content', 'templates', 'public'):
            (project / directory).mkdir()
        config = {'config': {'content-dir':'content/', 'content-ext':'.html',
            'output-dir':'public/', 'output-ext':'.html',
            'default-template':'templates/template.html', 'build-threads':1}}
        (project / '.nift/config.json').write_text(json.dumps(config))
        (project / '.nift/tracked.json').write_text(json.dumps({'tracked':[
            {'name':'sample','title':'Sample','template':'templates/template.html'}]}))
        (project / 'templates/template.html').write_text('@content')
        (project / 'content/sample.html').write_text(
            '$[posts := [{"title":"First","excerpt":"One"},'
            '{"title":"Second","excerpt":"Two"}]]\n' + code)
        subprocess.run([str(binary), 'build', '--all'], cwd=project, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result = (project / 'public/sample.html').read_text()
        assert result.count('<article>') == 2, result
        for expected in ('<h2>First</h2>', '<p>One</p>', '<h2>Second</h2>', '<p>Two</p>'):
            assert expected in result, result
    print('check-about-example passed: displayed colon-loop example renders both posts')

if __name__ == '__main__':
    main()
