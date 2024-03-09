create table "public"."Onboarding" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "greeting" text not null default ''::text,
    "quick_1" text,
    "quick_2" text,
    "quick_3" text
);


CREATE UNIQUE INDEX "Onboarding_pkey" ON public."Onboarding" USING btree (id);

alter table "public"."Onboarding" add constraint "Onboarding_pkey" PRIMARY KEY using index "Onboarding_pkey";


