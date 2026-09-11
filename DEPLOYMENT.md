# JNV MarkFlow deployment

This project is configured for Render with a managed PostgreSQL database.

## Vercel

The repository also contains `vercel.json` and `api/index.py` so the connected Vercel project can run Django as a Python function. In the Vercel project settings, add these environment variables for **Production**:

- `DJANGO_SECRET_KEY`: a long random secret
- `DJANGO_DEBUG`: `False`
- `DJANGO_ALLOWED_HOSTS`: `jnvekm.vercel.app`
- `CSRF_TRUSTED_ORIGINS`: `https://jnvekm.vercel.app`
- `DATABASE_URL`: a hosted PostgreSQL connection string
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `TEACHER_USERNAME`, `TEACHER_PASSWORD`

Vercel's filesystem is not persistent, so do not use the checked-in SQLite database for production data. Use PostgreSQL and run `python manage.py migrate` and `python manage.py seed_initial_data` once against that database. For a long-running Django service with managed database provisioning, the Render Blueprint below remains the simpler option.

## Deploy

1. Purchase `jnvernakulam.com` or use a domain registrar where you control DNS.
2. In Render, choose **New > Blueprint** and select the `JNV-EKM` GitHub repository.
3. Render reads `render.yaml`, creates the web service and PostgreSQL database, runs migrations, collects static files, and seeds classes 6A through 12B.
4. Set these secret environment variables in the Render web service:

   - `ADMIN_USERNAME`: `Admin@JNV`
   - `ADMIN_PASSWORD`: the requested admin password
   - `TEACHER_USERNAME`: `Teachers@JNV`
   - `TEACHER_PASSWORD`: the requested teacher password

5. Deploy the service and confirm the generated `onrender.com` URL opens `/login/`.

## Custom domain

1. In the Render service, open **Settings > Custom Domains**.
2. Add `marks.jnvernakulam.com`.
3. At the registrar DNS panel, create a CNAME record:

   - Name/host: `marks`
   - Target: the hostname Render displays for the service
   - Proxy: disabled while verifying, if the registrar offers a proxy toggle

4. Wait for DNS propagation. Render will issue the HTTPS certificate automatically.
5. Keep `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` aligned with the final domain.

Do not commit passwords or the production database URL. They belong in Render environment variables.
