#!/usr/bin/env python3
"""
Brand Vision High-Performance Dev Server (Threading + HTTP 206 Byte-Range Streaming)
Handles parallel asset fetching, fast video seeking without broken pipes, and static caching.
"""

import os
import re
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class RangeRequestHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler with HTTP 206 Partial Content (Byte Range) support."""

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        # Lightweight caching for images, videos, fonts, and stylesheets
        lower_path = self.path.lower()
        if any(lower_path.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.svg', '.mp4', '.webp', '.woff2', '.ttf', '.css', '.js')):
            self.send_header('Cache-Control', 'public, max-age=86400')
        super().end_headers()

    def send_head(self):
        range_header = self.headers.get('Range')
        if not range_header:
            return super().send_head()

        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        fs = os.fstat(f.fileno())
        total_length = fs.st_size

        match = re.match(r'^bytes=(\d*)-(\d*)$', range_header.strip())
        if not match:
            return super().send_head()

        start_str, end_str = match.groups()
        if start_str and end_str:
            start = int(start_str)
            end = int(end_str)
        elif start_str:
            start = int(start_str)
            end = total_length - 1
        elif end_str:
            start = total_length - int(end_str)
            end = total_length - 1
        else:
            return super().send_head()

        if start >= total_length or end >= total_length or start > end:
            self.send_error(HTTPStatus.RANGE_NOT_SATISFIABLE, "Requested Range Not Satisfiable")
            self.send_header('Content-Range', f'bytes */{total_length}')
            self.end_headers()
            f.close()
            return None

        length = end - start + 1
        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{total_length}')
        self.send_header('Content-Length', str(length))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()

        f.seek(start)
        self._range_length = length
        return f

    def copyfile(self, source, outputfile):
        length = getattr(self, '_range_length', None)
        if length is None:
            super().copyfile(source, outputfile)
            return

        bufsize = 64 * 1024
        remaining = length
        try:
            while remaining > 0:
                chunk = min(bufsize, remaining)
                data = source.read(chunk)
                if not data:
                    break
                outputfile.write(data)
                remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, format, *args):
        # Keep terminal log clean; only log errors
        if len(args) > 1 and str(args[1]) not in ('200', '206', '304'):
            super().log_message(format, *args)

def run(port=8000, directory=None):
    if directory:
        os.chdir(directory)
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, RangeRequestHandler)
    print(f"Brand Vision threaded server running at http://localhost:{port}/ (Range 206 supported)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port=port)
