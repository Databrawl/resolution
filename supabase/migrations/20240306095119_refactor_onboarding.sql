alter table "public"."Onboarding" drop constraint "Onboarding_pkey";

drop index if exists "public"."Onboarding_pkey";

drop table "public"."Onboarding";

create table "public"."onboarding" (
    "id" uuid not null default gen_random_uuid(),
    "org_id" uuid,
    "created_at" timestamp with time zone not null default now(),
    "greeting" text not null default ''::text,
    "quick_1" text,
    "quick_2" text,
    "quick_3" text
);


CREATE UNIQUE INDEX "Onboarding_pkey" ON public.onboarding USING btree (id);

alter table "public"."onboarding" add constraint "Onboarding_pkey" PRIMARY KEY using index "Onboarding_pkey";

alter table "public"."onboarding" add constraint "onboarding_org_id_fkey" FOREIGN KEY (org_id) REFERENCES org(id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."onboarding" validate constraint "onboarding_org_id_fkey";


