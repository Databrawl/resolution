create table "public"."alembic_version" (
    "version_num" character varying(32) not null
);


create table "public"."chat" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "user_id" uuid not null,
    "active" boolean not null default true
);


create table "public"."chunk" (
    "org_id" uuid not null,
    "data" json not null,
    "hash_value" character varying(64) not null,
    "embedding" vector(1536) not null,
    "id" uuid not null
);


create table "public"."message" (
    "id" uuid not null default gen_random_uuid(),
    "chat_id" uuid not null,
    "text" character varying not null,
    "author" character varying not null default 'human'::character varying,
    "created_at" timestamp with time zone not null default now()
);


create table "public"."org" (
    "name" character varying(30) not null,
    "id" uuid not null
);


create table "public"."org_user" (
    "user_id" uuid not null,
    "org_id" uuid not null,
    "id" uuid not null
);


CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num);

CREATE UNIQUE INDEX chat_pkey ON public.chat USING btree (id);

CREATE UNIQUE INDEX chunk_pkey ON public.chunk USING btree (id);

CREATE UNIQUE INDEX message_pkey ON public.message USING btree (id);

CREATE UNIQUE INDEX org_hash_unique_together ON public.chunk USING btree (org_id, hash_value);

CREATE UNIQUE INDEX org_pkey ON public.org USING btree (id);

CREATE UNIQUE INDEX org_user_pkey ON public.org_user USING btree (id);

alter table "public"."alembic_version" add constraint "alembic_version_pkc" PRIMARY KEY using index "alembic_version_pkc";

alter table "public"."chat" add constraint "chat_pkey" PRIMARY KEY using index "chat_pkey";

alter table "public"."chunk" add constraint "chunk_pkey" PRIMARY KEY using index "chunk_pkey";

alter table "public"."message" add constraint "message_pkey" PRIMARY KEY using index "message_pkey";

alter table "public"."org" add constraint "org_pkey" PRIMARY KEY using index "org_pkey";

alter table "public"."org_user" add constraint "org_user_pkey" PRIMARY KEY using index "org_user_pkey";

alter table "public"."chat" add constraint "chat_user_id_fkey" FOREIGN KEY (user_id) REFERENCES auth.users(id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."chat" validate constraint "chat_user_id_fkey";

alter table "public"."chunk" add constraint "chunk_org_id_fkey" FOREIGN KEY (org_id) REFERENCES org(id) ON DELETE CASCADE not valid;

alter table "public"."chunk" validate constraint "chunk_org_id_fkey";

alter table "public"."chunk" add constraint "org_hash_unique_together" UNIQUE using index "org_hash_unique_together";

alter table "public"."message" add constraint "message_chat_id_fkey" FOREIGN KEY (chat_id) REFERENCES chat(id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."message" validate constraint "message_chat_id_fkey";

alter table "public"."org_user" add constraint "org_user_org_id_fkey" FOREIGN KEY (org_id) REFERENCES org(id) ON DELETE CASCADE not valid;

alter table "public"."org_user" validate constraint "org_user_org_id_fkey";

alter table "public"."org_user" add constraint "org_user_user_id_fkey" FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE not valid;

alter table "public"."org_user" validate constraint "org_user_user_id_fkey";


