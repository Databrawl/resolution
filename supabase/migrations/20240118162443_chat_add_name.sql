create sequence "public"."test_tenant_id_seq";

create table "public"."test_tenant"
(
    "id"      integer not null default nextval('test_tenant_id_seq'::regclass),
    "details" text
);


alter table "public"."chat"
    add column "name" text not null default ''::text;

alter sequence "public"."test_tenant_id_seq" owned by "public"."test_tenant"."id";

CREATE UNIQUE INDEX test_tenant_pkey ON public.test_tenant USING btree (id);

alter table "public"."test_tenant"
    add constraint "test_tenant_pkey" PRIMARY KEY using index "test_tenant_pkey";


