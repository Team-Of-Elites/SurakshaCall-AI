# Mobile Audio Streaming Demo

This setup lets a phone browser act as the microphone while the laptop runs all SurakshaCall AI processing locally.

## One-time HTTPS certificate setup

Mobile browsers block microphone access on plain `http://` pages unless the page is `localhost`. Because the phone opens the laptop local IP, run the backend over HTTPS.

Preferred with `mkcert`:

```bash
brew install mkcert
mkcert -install
mkdir -p certs
LOCAL_IP=$(python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()")
mkcert -key-file certs/surakshacall-local-key.pem -cert-file certs/surakshacall-local-cert.pem localhost 127.0.0.1 "$LOCAL_IP"
```

Fallback with OpenSSL:

```bash
mkdir -p certs
LOCAL_IP=$(python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()")
cat > certs/surakshacall-local.cnf <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = dn

[dn]
CN = SurakshaCall Local

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
IP.2 = $LOCAL_IP
EOF
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/surakshacall-local-key.pem \
  -out certs/surakshacall-local-cert.pem \
  -config certs/surakshacall-local.cnf
```

The phone will show a warning the first time because the cert is local/self-signed. Before the demo, open the pairing URL once on the phone, tap `Advanced`, then `Proceed`. Keep that accepted tab/session ready.

## Run backend over HTTPS

```bash
LOCAL_IP=$(python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()")
LOCAL_NETWORK_MODE=true BACKEND_HOST="$LOCAL_IP" uvicorn backend.app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-keyfile certs/surakshacall-local-key.pem \
  --ssl-certfile certs/surakshacall-local-cert.pem
```

This works on normal WiFi and on the phone hotspot because the backend detects the active local IP at runtime.

## Pair phone

Create a session:

```bash
curl -k -X POST https://127.0.0.1:8000/api/sessions
```

Get the phone URL:

```bash
curl -k https://127.0.0.1:8000/api/v1/sessions/<session_id>/qr
```

Open the `pairing_url` on the phone, accept the certificate warning once, then tap `Start Listening`.

## Queue connection

`mobile_pairing.py` sends incoming binary WebSocket PCM frames into:

```text
app.state.audio_queues -> backend.app.audio.queues.AudioQueueRegistry
```

The queue stores `AudioFrame` objects keyed by `session_id`. `MobileAudioTranscriptionService` reads that same queue, transcribes with `faster-whisper`, and submits text into the existing `SessionManager.submit_transcript()` path, so downstream fast detection, risk updates, dashboard, and mobile warnings stay shared.

## Audio contract

- Input socket: `wss://<laptop-ip>:8000/ws/mobile/{session_id}`
- Binary frames: 16kHz mono Int16 PCM
- Control messages: JSON text on the same socket
- Backend resampling: none
- Processing location: laptop only
