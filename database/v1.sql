

create table if not exists `packages`
(
    id         bigint auto_increment
        primary key,
    name       varchar(100) not null,
    profile    varchar(100) not null,
    admin_id   varchar(100) not null,
    router_id   varchar(100) not null,
    status     int          null,
    created_at datetime(6)  null,
    created_by int          not null,
    updated_at datetime(6)  null,
    updated_by int          not null,
    constraint name
        unique (name)
);
