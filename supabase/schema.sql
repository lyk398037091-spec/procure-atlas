-- ProcureAtlas production schema (Phase 2)
-- Run in a dedicated Supabase project. MVP GitHub Pages does not require this yet.
create extension if not exists pgcrypto;

create table if not exists manufacturers (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  legal_name text not null,
  display_name text not null,
  website text,
  city text,
  province text,
  country_code text not null default 'CN',
  founded_year int,
  profile_status text not null default 'public_source',
  audit_status text not null default 'not_audited',
  summary text,
  last_reviewed_at timestamptz,
  published boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  category text not null,
  description text,
  published boolean not null default true
);

create table if not exists capabilities (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  capability_group text not null,
  published boolean not null default true
);

create table if not exists applications (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  description text,
  published boolean not null default true
);

create table if not exists manufacturer_products (
  manufacturer_id uuid not null references manufacturers(id) on delete cascade,
  product_id uuid not null references products(id) on delete cascade,
  state text not null default 'evidenced',
  primary key (manufacturer_id, product_id)
);

create table if not exists manufacturer_capabilities (
  manufacturer_id uuid not null references manufacturers(id) on delete cascade,
  capability_id uuid not null references capabilities(id) on delete cascade,
  state text not null default 'evidenced',
  primary key (manufacturer_id, capability_id)
);

create table if not exists manufacturer_applications (
  manufacturer_id uuid not null references manufacturers(id) on delete cascade,
  application_id uuid not null references applications(id) on delete cascade,
  primary key (manufacturer_id, application_id)
);

create table if not exists evidence (
  id uuid primary key default gen_random_uuid(),
  manufacturer_id uuid not null references manufacturers(id) on delete cascade,
  claim_key text not null,
  claim_text text not null,
  source_url text not null,
  source_type text not null,
  checked_at date not null,
  confidence text not null check (confidence in ('A','B','C','U')),
  review_state text not null default 'approved' check (review_state in ('suggested','approved','rejected','stale')),
  evidence_excerpt text,
  created_at timestamptz not null default now()
);

create table if not exists rfqs (
  id uuid primary key default gen_random_uuid(),
  buyer_email text not null,
  buyer_company text not null,
  target_country text,
  product_id uuid references products(id),
  application_text text,
  quantity_text text,
  requirements text not null,
  status text not null default 'new',
  created_at timestamptz not null default now()
);

create index if not exists manufacturers_published_idx on manufacturers(published, province);
create index if not exists evidence_manufacturer_idx on evidence(manufacturer_id, review_state, checked_at desc);
create index if not exists rfqs_created_idx on rfqs(created_at desc);

alter table manufacturers enable row level security;
alter table products enable row level security;
alter table capabilities enable row level security;
alter table applications enable row level security;
alter table manufacturer_products enable row level security;
alter table manufacturer_capabilities enable row level security;
alter table manufacturer_applications enable row level security;
alter table evidence enable row level security;
alter table rfqs enable row level security;

-- Public reads only expose published catalogue data.
create policy "public read published manufacturers" on manufacturers for select using (published = true);
create policy "public read products" on products for select using (published = true);
create policy "public read capabilities" on capabilities for select using (published = true);
create policy "public read applications" on applications for select using (published = true);
create policy "public read manufacturer products" on manufacturer_products for select using (true);
create policy "public read manufacturer capabilities" on manufacturer_capabilities for select using (true);
create policy "public read manufacturer applications" on manufacturer_applications for select using (true);
create policy "public read approved evidence" on evidence for select using (review_state = 'approved');

-- Deliberately no anonymous RFQ INSERT policy yet.
-- Add a protected Edge Function + Turnstile/rate limiting before enabling production RFQ submission.
