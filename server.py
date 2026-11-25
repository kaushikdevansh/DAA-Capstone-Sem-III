import hashlib
import hmac
import json
import secrets
import threading
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from courier.generator import generate
from courier.planner import plan

ROOT = Path(__file__).resolve().parent
USER_FILE = ROOT / "users.json"
ITERATIONS = 240000
SESSION_TTL = 43200
sessions = {}
user_lock = threading.Lock()


def read_users():
    if not USER_FILE.exists():
        return {}
    with USER_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def write_users(users):
    temporary = USER_FILE.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=2)
    temporary.replace(USER_FILE)


def password_record(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS).hex()
    return {"salt": salt, "digest": digest}


def password_matches(password, record):
    candidate = password_record(password, record["salt"])["digest"]
    return hmac.compare_digest(candidate, record["digest"])


class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200, cookie=None):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def get_session(self):
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        morsel = cookie.get("routewise_session")
        token = morsel.value if morsel else ""
        session = sessions.get(token)
        if not session:
            return None, None
        if session["expires"] <= time.time():
            sessions.pop(token, None)
            return None, None
        return token, session

    def require_session(self):
        _, session = self.get_session()
        if session:
            return session
        self.send_json({"error": "Please sign in to use the planner."}, 401)
        return None

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/session":
            _, session = self.get_session()
            self.send_json({"authenticated": bool(session), "email": session["email"] if session else None})
            return
        if path == "/api/sample":
            if not self.require_session():
                return
            with (ROOT / "data" / "sample.json").open(encoding="utf-8") as file:
                self.send_json(json.load(file))
            return
        if path == "/" or path in ("/index.html", "/app.js", "/styles.css"):
            name = "index.html" if path == "/" else path[1:]
            file_path = ROOT / "web" / name
            content_type = {
                ".html": "text/html; charset=utf-8",
                ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8"
            }[file_path.suffix]
            body = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 2_000_000:
                self.send_json({"error": "Request is too large."}, 413)
                return
            payload = json.loads(self.rfile.read(length))
            path = urlparse(self.path).path

            if path in ("/api/register", "/api/login"):
                self.handle_auth(path, payload)
                return
            if path == "/api/logout":
                token, _ = self.get_session()
                if token:
                    sessions.pop(token, None)
                self.send_json({"authenticated": False}, cookie="routewise_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0")
                return
            if path not in ("/api/generate", "/api/plan"):
                self.send_error(404)
                return
            if not self.require_session():
                return

            if path == "/api/generate":
                data = generate(
                    int(payload.get("nodes", 18)),
                    int(payload.get("parcels", 40)),
                    int(payload.get("capacity", 60)),
                    int(payload.get("seed", 1))
                )
            else:
                data = payload.get("data", payload)
            result = plan(data, int(payload.get("exact_limit", 12)))
            self.send_json({"input": data, "result": result})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, 400)
        except Exception as error:
            self.send_json({"error": str(error)}, 500)

    def handle_auth(self, path, payload):
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", ""))
        if len(email) > 254 or "@" not in email or email.startswith("@") or email.endswith("@"):
            self.send_json({"error": "Enter a valid email address."}, 400)
            return
        if path == "/api/register" and len(password) < 8:
            self.send_json({"error": "Use a password with at least 8 characters."}, 400)
            return
        with user_lock:
            users = read_users()
            if path == "/api/register":
                if email in users:
                    self.send_json({"error": "An account with this email already exists."}, 409)
                    return
                users[email] = password_record(password)
                write_users(users)
            elif email not in users or not password_matches(password, users[email]):
                self.send_json({"error": "Email or password is incorrect."}, 401)
                return
        token = secrets.token_urlsafe(32)
        sessions[token] = {"email": email, "expires": time.time() + SESSION_TTL}
        cookie = f"routewise_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_TTL}"
        self.send_json({"authenticated": True, "email": email}, cookie=cookie)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Routewise Courier Planner is running at http://127.0.0.1:8000")
    server.serve_forever()
