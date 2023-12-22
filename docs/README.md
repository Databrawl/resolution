# Dumping initial PostgreSQL schema with Supabase generated tables:

```bash
pg_dump -h localhost -p 54322 -U postgres -d postgres --schema-only --no-owner --no-acl > init.sql
```

I still had to remove some objects that were created somehow and thus caused duplication errors:

```sql
    CREATE FUNCTION vault.secrets_encrypt_secret_secret() RETURNS trigger
        LANGUAGE plpgsql
        AS $$
            BEGIN
                    new.secret = CASE WHEN new.secret IS NULL THEN NULL ELSE
                CASE WHEN new.key_id IS NULL THEN NULL ELSE pg_catalog.encode(
                  pgsodium.crypto_aead_det_encrypt(
                    pg_catalog.convert_to(new.secret, 'utf8'),
                    pg_catalog.convert_to((new.id::text || new.description::text || new.created_at::text || new.updated_at::text)::text, 'utf8'),
                    new.key_id::uuid,
                    new.nonce
                  ),
                    'base64') END END;
            RETURN new;
            END;
            $$;

    CREATE VIEW vault.decrypted_secrets AS
     SELECT secrets.id,
        secrets.name,
        secrets.description,
        secrets.secret,
            CASE
                WHEN (secrets.secret IS NULL) THEN NULL::text
                ELSE
                CASE
                    WHEN (secrets.key_id IS NULL) THEN NULL::text
                    ELSE convert_from(pgsodium.crypto_aead_det_decrypt(decode(secrets.secret, 'base64'::text), convert_to(((((secrets.id)::text || secrets.description) || (secrets.created_at)::text) || (secrets.updated_at)::text), 'utf8'::name), secrets.key_id, secrets.nonce), 'utf8'::name)
                END
            END AS decrypted_secret,
        secrets.key_id,
        secrets.nonce,
        secrets.created_at,
        secrets.updated_at
       FROM vault.secrets;
```

# Database session architecture

Using `scoped_session` didn't work since this object keeps references to the initial DB URL in factories.
Besides, it's an unnecessary complexity, as we can simply store the session in the context variable.