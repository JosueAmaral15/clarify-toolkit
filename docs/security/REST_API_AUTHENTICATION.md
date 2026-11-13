# REST API Authentication

The experimental REST API is not currently wired to the Clarify GUI or CLI. It
must be embedded explicitly. Creating `ClarifyAPI` now fails closed unless the
`CLARIFY_API_TOKEN` environment variable contains a 32-512 byte printable ASCII
token.

Do not place the token in source code, command-line arguments, logs or committed
configuration. Enter it through a protected service environment or an
interactive secret prompt. Clients send it only in the authorization header:

```text
Authorization: Bearer <token>
```

`GET /status` remains unauthenticated because it returns only the fixed
`{"status":"ok"}` health response and never accesses application state.
`GET /json` and `POST /translate` require authentication. Translation accepts
only `json` and `lang`; undeclared fields are rejected.

The default listener is loopback-only (`127.0.0.1`). A non-loopback host also
requires the embedding code to pass `allow_remote=True` explicitly. Remote use
must additionally be placed behind TLS so the Bearer token is not exposed in
transit.
