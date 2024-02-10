alter table "public"."message" drop column "author";

alter table "public"."message" drop column "text";

alter table "public"."message" add column "ai_message" text;

alter table "public"."message" add column "user_message" text not null;


