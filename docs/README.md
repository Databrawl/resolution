# Dumping initial PostgreSQL auth schema with Supabase generated tables:

```bash
pg_dump -h localhost -p 54322 -U postgres -d postgres -n auth --schema-only --no-owner --no-acl > init_auth.sql
```