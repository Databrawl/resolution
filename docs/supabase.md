# Supabase related commands

## Create a migration

1. First, edit the tables in the local UI or directly in the database.
2. Then, run the following command to create a migration:
    ```bash
      scripts/add_migration.sh
    ```
3. Add the migration to Git
4. Push the migration to the remote database

   While supabase CLI [isn't updated to support IPv6](https://github.com/supabase/cli/issues/1625),
   use this command:
   ```bash
   npx supabase@beta db push --db-url postgresql://postgres.khbybtymvfmhdakalayr:oNGhdBRtaaOUEHfe@aws-0-us-east-1.pooler.supabase.com:5432
   ```
