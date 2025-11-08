create table if not exists teams(
  team_id int primary key,
  name text not null
);

create table if not exists players(
  player_id int primary key,
  name text not null,
  team_id int references teams(team_id)
);

create table if not exists fixtures(
  fixture_id int primary key,
  date_utc timestamptz not null,
  league_id int not null,
  season int not null,
  home_id int references teams(team_id),
  away_id int references teams(team_id),
  venue text,
  referee text,
  status text
);
create index if not exists fixtures_date_idx on fixtures(date_utc);

create table if not exists team_stats(
  fixture_id int references fixtures(fixture_id),
  team_id int references teams(team_id),
  goals int,
  xg numeric,
  shots int,
  shots_on_target int,
  corners int,
  cards_yellow int,
  cards_red int,
  fouls int,
  primary key (fixture_id, team_id)
);

create table if not exists player_stats(
  fixture_id int references fixtures(fixture_id),
  player_id int references players(player_id),
  team_id int references teams(team_id),
  minutes int,
  shots int,
  shots_on_target int,
  fouls_committed int,
  fouls_drawn int,
  cards_yellow int,
  saves int,
  primary key (fixture_id, player_id)
);

create table if not exists model_artifacts(
  name text primary key,
  fitted_at timestamptz not null,
  blob bytea not null
);

create table if not exists match_predictions(
  fixture_id int primary key references fixtures(fixture_id),
  home_win double precision,
  draw double precision,
  away_win double precision,
  btts double precision,
  over25 double precision,
  under25 double precision,
  exp_home_goals double precision,
  exp_away_goals double precision,
  exp_corners double precision,
  exp_cards double precision,
  generated_at timestamptz default now()
);

create table if not exists player_projections(
  fixture_id int references fixtures(fixture_id),
  player_id int references players(player_id),
  metric text,
  mean double precision,
  p50 double precision,
  p90 double precision,
  prob_ge1 double precision,
  prob_ge2 double precision,
  generated_at timestamptz default now(),
  primary key (fixture_id, player_id, metric)
);
