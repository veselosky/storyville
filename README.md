# Storyville: Vince's little corner of the web

This Django project houses my actively maintained websites.

## Environment: Local vs Docker

Default values in the project's `settings.py` are suitable for running inside a Docker
container. For developing locally (running the app on local host and not in a Docker
container) copy the `example.env` file to `.env` within the project base directory and
adjust variables accordingly.

To simplify both development and production, data files that need backing up are stored
together under a single directory, designated by the `DATA_DIR` environment variable.
The SQLite database files are stored under `$DATA_DIR/db/`. STATIC_ROOT and MEDIA_ROOT
are subdirectories stored under `$DATA_DIR/www`.

In the Docker container, `DATA_DIR` has the default value of `/app/var/`. To run under
Docker, provide two volumes or bind mounts, one for `/app/var/db/`, and a second for
`/app/var/www/`. The www volume/mount must be shared with your web server to serve
static files and media.

When running in a Docker container, several environment variables MUST be provided:

- SECRET_KEY - App will not run without it.
- ALLOWED_HOSTS - For dev, set to "\*". For production, the sites you will serve.
- SITE_ID - Not required for production (assuming DNS is correct), but needed for local
  dev.
- CACHE_URL - Using the example compose file, set to `redis://redis:6379/0`

TODO: Automate building container image on release
