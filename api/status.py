from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs

# Import the jobs dictionary from the process_audio module 
from api.process_audio import jobs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            query_params = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            job_id = query_params.get('id', [''])[0]
            
            if not job_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No job ID provided"}).encode())
                return
            
            # Get job status
            job_info = jobs.get(job_id)
            
            if not job_info:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Job not found"}).encode())
                return
            
            # Return job status
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(job_info).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()